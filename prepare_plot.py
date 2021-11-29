from datetime import date
from datetime import datetime
from datetime import timedelta
import pandas as pd
from common import Constants


def prepare_normal(line_name):
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
    return df

def fix_next_days(df, col):
    midnight = pd.Timestamp.today().replace(
        hour=0, minute=0, second=0, microsecond=0, nanosecond=0
    )
    three_am = pd.Timestamp.today().replace(
        hour=3, minute=0, second=0, microsecond=0, nanosecond=0
    )
    for train in df.Train.unique():
        xs = df[df.Train == train][col]
        xs_dropped = xs.dropna()
        to_change = (midnight <= xs_dropped) & (xs_dropped < three_am)
        new = xs_dropped[to_change].apply(lambda x: x + timedelta(days=1))
        if new.shape[0] == 0:
            continue
        df.loc[new.index[0] : new.index[-1], col] = new

def prepare_delta(df):
    print('Preparing delta plot (offline)...')

    grouped = df.groupby('Train')
    def g(here):
        new = here.Arrive.apply(lambda x: x - here.Arrive.min())
        here['Arrive'] = new
        return here

    def f(here):
        first_station = here.iloc[0].Station
        dup_firsts = here[here.Station == first_station]
        if dup_firsts.shape[0] > 1:
            start_idx = dup_firsts.iloc[1:].index[0]
            # This will mutate grouped...
            new = here.loc[start_idx:].Train.apply(lambda x: x + '_1')
            here.loc[start_idx:].Train = new
            res1 = g(here.loc[:start_idx-1])
            res2 = g(here.loc[start_idx:])
            return pd.concat([res1, res2])
        return g(here)

    grouped = grouped.apply(f)
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    grouped['Arrive'] = grouped.Arrive.apply(lambda x: midnight + x)
    return grouped

