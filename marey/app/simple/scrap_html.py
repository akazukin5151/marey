import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from .common import mkdirs_touch_open, Constants

def main(line_name):
    outfile = Constants.gen_csv_dir / f'{line_name}.csv'
    if outfile.exists():
        return
    print('Scraping html... (offline)')
    df = pd.DataFrame(columns=['Station', 'Arrive', 'Depart', 'Train'])
    for f in (Constants.html_dir / line_name).iterdir():
        df = df.append(make_df(f))
    mkdirs_touch_open('', outfile)
    df.to_csv(outfile, index=False)

def make_df(file_):
    with open(file_, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    first_station = soup.find_all('div', class_='result-route-departure-wrap')[0]
    rest_stations = soup.find_all('div', class_='result-route-transfer-wrap')

    # first and last stations only have one of {arrival, departure} time
    first_station_name = get_station_name(first_station)
    # don't special-case this because a "first" station can actually not be the terminus
    _, first_station_dep_time, _ = get_rest_station_info(first_station)
    first_station_info = (first_station_name, np.nan, first_station_dep_time)

    last_station_name = get_station_name(rest_stations[-1])
    last_station_arr_time = get_station_time_text(rest_stations[-1]).strip()[:-1]
    last_station_info = (last_station_name, last_station_arr_time, np.nan)

    final = [
        get_rest_station_info(x)
        for x in rest_stations[:-1]
        # if the first station isn't the terminus, exclude previous stations
        if x.parent.parent.parent['class'][0] != 'before-selected-station'
    ]
    final = [first_station_info] + final + [last_station_info]
    final = pd.DataFrame.from_records(final, columns=['Station', 'Arrive', 'Depart'])
    final['Train'] = file_.name
    return final.reset_index()

def get_station_name(s):
    return s.find('td', class_='td-station-name').get_text()

def get_station_time_text(s):
    return s.find('td', class_='td-dep-and-arr-time').get_text()

def get_rest_station_info(s):
    name = get_station_name(s)
    # can filter out empty strings, but let's just assume the arrival and departure time
    # is the 1st and last items respectively
    splitted = get_station_time_text(s).strip().split('\t')
    arr_t = splitted[0].strip()[:-1]
    dep_t = splitted[-1].strip()[:-1]
    return (name, arr_t, dep_t)
