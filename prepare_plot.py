from datetime import date
from datetime import datetime
from datetime import timedelta
import pandas as pd


def prepare_normal(line_name):
    print('Preparing plot (offline)...')
    df = pd.read_csv(f'out/generated_csv/{line_name}.csv')

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

    # Move the midnight train to the right (pretend it's a day later)
    train = df.sort_values('Arrive').iloc[0].Train
    start = df[df.Train == train].iloc[0].name
    end = df[df.Train == train].iloc[-1].name
    df.loc[start:end, 'Arrive'] += timedelta(days=1)
    df.loc[start:end, 'Depart'] += timedelta(days=1)

    # Fill NaT in Arrive with Depart
    # Only the first station has NaT for Arrive
    # This assumes that there's only one first-station, so picking the first one is fine
    first = df[df['index'] == 0].Station.iloc[0]
    df['Arrive'].where(
        df['Station'] != first, df.Depart, inplace=True
    )
    return df

def fix_next_days(df, col):
    for train in df.Train.unique():
        xs = df[df.Train == train].Arrive
        if not xs.dropna().is_monotonic:
            xx = find_next_day(xs.dropna())
            pos = xs[xs == xx].index[0]
            df.loc[pos : xs.index[-1], col] = (
                df.loc[pos : xs.index[-1], col] + timedelta(days=1)
            )

def find_next_day(xs: '[a]') -> 'a':
    '''uses binary search to find the point where the next day has started'''
    # base case 1
    # is_monotonic tests if it is monotonically INCREASING
    # that means [3, 4].is_monotonic is FALSE, and therefore the culprit is 4
    if not xs.is_monotonic and len(xs) == 2:
        return xs.iloc[-1]

    # split up the list into two halves
    mid = len(xs) // 2
    upper = xs[:mid]
    if upper.is_monotonic:
        lower = xs[mid:]
        if lower.is_monotonic:
            # base case 2
            # if both are monotonic, then we've found the break
            return xs.iloc[mid]
        # recursive case 1
        # if the upper is monotonic, then it means the lower half is not
        # repeat with lower
        return find_next_day(lower)
    # recursive case 2
    # if the upper is not monotonic, repeat with upper
    return find_next_day(upper)

def prepare_delta(df):
    print('Preparing delta plot (offline)...')
    for train in df.Train.unique():
        here = df[df.Train == train]
        # this doesn't work for some fucking reason
        #new = here.Arrive - here.Arrive.min()
        new = here.Arrive.apply(lambda x: x - here.Arrive.min())
        df['Arrive'].where(df.Train != train, new, inplace=True)
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    df['Arrive'] = df.Arrive.apply(lambda x: midnight + x)

