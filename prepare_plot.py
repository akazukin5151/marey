from datetime import timedelta
import pandas as pd
import numpy as np
from common import Constants


def prepare_normal(line_name):
    outfile = Constants.gen_csv_dir / f'{line_name}_processed.csv'
    if outfile.exists():
        return pd.read_csv(outfile, parse_dates=['Arrive', 'Depart'])

    print('Preparing plot (offline)...')

    df = pd.read_csv(Constants.gen_csv_dir / f'{line_name}.csv')

    df['Arrive'] = df.Arrive.str.replace('24:', '0:').astype('datetime64[ns]')
    df['Depart'] = df.Depart.astype('datetime64[ns]')

    # include dwell time
    new_rows = []
    for idx, row in df[df.Arrive != df.Depart].dropna().iterrows():
        new_row = row.copy()
        new_row['index'] += 0.5
        new_row['Arrive'] = new_row.Depart
        df.loc[idx, 'Depart'] = row['Arrive']
        new_rows.append(new_row)
    df = df.append(pd.DataFrame(new_rows)).reset_index(drop=True)
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
    df.to_csv(outfile)
    return df

def fix_next_days(df, col):
    midnight_ = pd.Timestamp.today().replace(
        hour=0, minute=0, second=0, microsecond=0, nanosecond=0
    )
    three_am = pd.Timestamp.today().replace(
        hour=3, minute=0, second=0, microsecond=0, nanosecond=0
    )
    for train in df.Train.unique():
        xs = df[df.Train == train][col]
        xs_dropped = xs.dropna()
        to_change = (midnight_ <= xs_dropped) & (xs_dropped < three_am)
        new = xs_dropped[to_change].apply(lambda x: x + timedelta(days=1))
        if new.shape[0] == 0:
            continue
        df.loc[new.index[0] : new.index[-1], col] = new

def subtract_min(here):
    new = here.Arrive.apply(lambda x: x - here.Arrive.min())
    here['Arrive'] = new
    return here

def groupby_apply_midnight(df: 'DataFrame[a]', f: '(a -> b)') -> 'DataFrame[b]':
    '''Map a function over a dataframe grouped by trains, then added by midnight'''
    grouped = df.groupby('Train')
    grouped = grouped.apply(f)
    grouped['Arrive'] = grouped.Arrive.apply(lambda x: Constants.midnight + x)
    return grouped

def prepare_delta(line_name, df):
    outfile = Constants.gen_csv_dir / f'{line_name}_delta.csv'
    if outfile.exists():
        return pd.read_csv(outfile, parse_dates=['Arrive', 'Depart'])

    print('Preparing delta plot (offline)...')

    def f(here):
        first_station = here.iloc[0].Station
        dup_firsts = here[here.Station == first_station]
        if dup_firsts.shape[0] > 1:
            start_idx = dup_firsts.iloc[1:].index[0]
            # This will mutate grouped...
            new = here.loc[start_idx:].Train.apply(lambda x: x + '_1')
            here.loc[start_idx:].Train = new
            res1 = subtract_min(here.loc[:start_idx - 1])
            res2 = subtract_min(here.loc[start_idx:])
            return pd.concat([res1, res2])
        return subtract_min(here)

    grouped = groupby_apply_midnight(df, f)
    grouped.to_csv(outfile)

    return grouped

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
    branched = {}
    for (a, b) in branch_data:
        branched[a] = branched[b] = a + '/' + b
    return branched

def split_by_branch(df):
    stations_in_each_trip = df.groupby('Train').Station.unique().apply(tuple)
    unique_counts = stations_in_each_trip.value_counts()
    main_line = unique_counts.index[0]
    branch_lines = []
    for unique_line, _ in unique_counts[1:].items():
        if not (set(unique_line).issubset(main_line)
                or set(main_line).issubset(unique_line)):
            branch_lines.append(unique_line)

    trains_on_main = stations_in_each_trip[~stations_in_each_trip.isin(branch_lines)]
    df_for_main = df[df.Train.isin(trains_on_main.index)]
    # TODO multiple branches?
    trains_on_branch = stations_in_each_trip[stations_in_each_trip.isin(branch_lines)]
    df_for_branch = df[df.Train.isin(trains_on_branch.index)]
    return (df_for_main, df_for_branch)

def set_station_seqs(df, branched):
    # FIXME: there's a setting with copy warning even though i always used .loc
    df.loc[:, 'Station_sequence'] = np.nan
    def f(x):
        for idx, row in x.iterrows():
            station = row.Station
            seq = branched.get(station, station)
            df.loc[idx, 'Station_sequence'] = seq
    df.groupby('Train').apply(f)
