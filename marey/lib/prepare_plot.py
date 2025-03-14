from pathlib import Path
from datetime import timedelta
from .common import Constants
import pandas as pd
import numpy as np


def prepare_normal(in_csv: Path, out_csv: Path):
    if out_csv.exists():
        return pd.read_csv(out_csv, parse_dates=['Arrive', 'Depart'])

    print('Preparing plot (offline)...')

    df = pd.read_csv(in_csv)

    df['Arrive'] = df.Arrive.str.replace('24:', '0:').astype('datetime64[ns]')
    df['Depart'] = df.Depart.astype('datetime64[ns]')
    df = df.reset_index()

    # include dwell time
    new_rows = []
    for idx, row in df[df.Arrive != df.Depart].dropna().iterrows():
        # create a new row to represent the departure dot
        # (where both times are the departure time)
        depart_dot = row.copy()
        depart_dot['index'] += 0.5
        depart_dot['Arrive'] = depart_dot.Depart
        # change the current row to represent the arrival dot
        # (where both times are the arrival time)
        df.loc[idx, 'Depart'] = row['Arrive']
        new_rows.append(depart_dot)
    df = pd.concat([df, pd.DataFrame(new_rows)]).reset_index(drop=True)
    df.sort_values(['Train', 'index'], inplace=True)

    fix_next_days(df, 'Arrive')
    fix_next_days(df, 'Depart')

    # Fill NaT in Arrive with Depart
    # Only the first station has NaT for Arrive
    # This assumes that there's only one first-station, so picking the first one is fine
    first = df[df['index'] == 0].Station.iloc[0]
    df['Arrive'].where(
        df['Station'] != first, df.Depart, inplace=True
    )
    df.to_csv(out_csv)
    return df

def fix_next_days(df, col):
    midnight_ = pd.Timestamp.today().replace(
        hour=0, minute=0, second=0, microsecond=0, nanosecond=0
    )
    three_am = pd.Timestamp.today().replace(
        hour=3, minute=0, second=0, microsecond=0, nanosecond=0
    )
    xs = df[col]
    xs_dropped = xs.dropna()
    to_change = (midnight_ <= xs_dropped) & (xs_dropped < three_am)
    for i in xs_dropped[to_change].index:
        df.loc[i, col] += timedelta(days=1)

def subtract_min(here):
    # no inplace to allow further processing
    new = here.Arrive.apply(lambda x: x - here.Arrive.min())
    here['Arrive'] = new
    return here

def groupby_apply_midnight(df: 'DataFrame[a]', f: '(a -> b)') -> 'DataFrame[b]':
    '''Map a function over a dataframe grouped by trains, then added by midnight'''
    grouped = df.groupby('Train')
    grouped = grouped.apply(f)
    # inplace not supported here
    grouped['Arrive'] = grouped.Arrive.apply(lambda x: Constants.midnight + x)
    return grouped

def prepare_delta(line_name, df):
    outfile = Constants.gen_csv_dir / f'{line_name}_delta.csv'
    if outfile.exists():
        return pd.read_csv(outfile, parse_dates=['Arrive', 'Depart'])

    print('Preparing delta plot (offline)...')

    # TODO: An alternative way would be to first identify loops
    # and append '_1' to their train name so that they appear to be a different train
    # then create a column of 'min for this train'
    # then subtract all values by that column
    # Also consider the other usage of groupby_apply_midnight
    grouped = groupby_apply_midnight(df, loop_aware_subtract_min)
    grouped.to_csv(outfile)
    return grouped

def loop_aware_subtract_min(here: 'DataFrame') -> 'DataFrame':
    '''This subtracts all times with the minimum time (shifting all values to 0)
    It handle loops (when a train passes through the same starting station twice)
    by treating the two separate loops as if they were two separate trains
    Only works if there is one loop (one repetition)
    '''
    first_station = here.iloc[0].Station
    dup_firsts = here[here.Station == first_station]
    if dup_firsts.shape[0] > 1:
        start_idx = dup_firsts.iloc[1:].index[0]
        # Append '_1' to the loop, so it appears to be a separate train
        # XXX: This will mutate the groupby, not sure if good idea
        new = here.loc[start_idx:].Train.apply(lambda x: x + '_1')
        here.loc[start_idx:].Train = new
        # Subtract minimums separately, so the first station in the loop
        # has time = 0
        res1 = subtract_min(here.loc[:start_idx - 1])
        res2 = subtract_min(here.loc[start_idx:])
        # Combine them again
        return pd.concat([res1, res2])
    return subtract_min(here)


def handle_branches(df, line):
    outfile1 = Constants.gen_csv_dir / f'{line.name}_main.csv'
    outfile2 = Constants.gen_csv_dir / f'{line.name}_branch.csv'
    if outfile1.exists() and outfile2.exists():
        return (
            pd.read_csv(outfile1, parse_dates=['Arrive', 'Depart']),
            pd.read_csv(outfile2, parse_dates=['Arrive', 'Depart'])
        )

    df_for_main, df_for_branch = split_by_branch(df)
    branched = branch_data_to_combined(line.branch_data)
    set_station_seqs(df_for_main, branched)
    set_station_seqs(df_for_branch, branched)

    df_for_main.to_csv(outfile1)
    df_for_branch.to_csv(outfile2)
    return (df_for_main, df_for_branch)

def branch_data_to_combined(branch_data: 'List[(str, str)]') -> 'dict[str, str]':
    '''For every station-on-main-line and station-on-branch-line pair,
    associate both to 'station-on-main-line / station-on-branch-line'
    '''
    # Cannot use dict comprehension because there are two insertions per loop
    branched = {}
    for (a, b) in branch_data:
        branched[a] = branched[b] = a + '/' + b
    return branched

def split_by_branch(df: 'DataFrame') -> 'Tuple[DataFrame, DataFrame]':
    '''Splits a DataFrame into one with only trains on the main line
    and the other with only trains on a branch line
    Only one branch supported
    '''
    # Take the most frequent sequence of stations and treat that as the main line
    stations_in_each_trip = df.groupby('Train').Station.unique().apply(tuple)
    unique_counts = stations_in_each_trip.value_counts()
    main_line = unique_counts.index[0]
    # A branch line is defined as a sequence that is not a subset of the main line
    # or the main line is not a subset of the sequence
    branch_lines = [
        unique_line
        for unique_line, _ in unique_counts[1:].items()
        if not (set(unique_line).issubset(main_line)
                or set(main_line).issubset(unique_line))
    ]

    trains_on_main = stations_in_each_trip[~stations_in_each_trip.isin(branch_lines)]
    df_for_main = df[df.Train.isin(trains_on_main.index)]
    # TODO multiple branches?
    trains_on_branch = stations_in_each_trip[stations_in_each_trip.isin(branch_lines)]
    df_for_branch = df[df.Train.isin(trains_on_branch.index)]
    return (df_for_main, df_for_branch)

def set_station_seqs(df, branched: 'dict[str, str]'):
    '''Renames main-branch station pairs'''
    df.loc[:, 'Station_sequence'] = np.nan
    def f(x):
        for idx, row in x.iterrows():
            station = row.Station
            seq = branched.get(station, station)
            df.loc[idx, 'Station_sequence'] = seq
    df.groupby('Train').apply(f)
