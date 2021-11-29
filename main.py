from enum import Enum
from pathlib import Path
from common import Constants, Line
import save_page
import get_urls
import download
import scrap_html
import prepare_plot
import plot

# (DataFrame -> DataFrame -> str -> str -> float -> str -> bool -> IO (), str)
class Plotter(Enum):
    matplotlib = (plot.matplotlib, 'png')
    bokeh      = (plot.bokeh,      'html')
    altair     = (plot.altair,     'html')

def main(line: Line, plotter: Plotter):
    save_page.main(line.url, line.name)
    get_urls.main(line.url, line.name)
    download.main(line.name)
    scrap_html.main(line.name)

    # Check if plot needs to be prepared
    ext = plotter.value[1]
    normal = Constants.plot_dir / f'{line.name}_normal.{ext}'
    delta = Constants.plot_dir / f'{line.name}_delta.{ext}'
    delta_scatter = Constants.plot_dir / f'{line.name}_delta_scatter.{ext}'
    if normal.exists() and delta.exists() and delta_scatter.exists():
        return

    df = prepare_plot.prepare_normal(line.name)

    stations_in_each_trip = df.groupby('Train').Station.unique().apply(tuple)
    unique_counts = stations_in_each_trip.value_counts()
    main_line = unique_counts.index[0]
    main_lines = [main_line]
    branch_lines = []
    for unique_line, _ in unique_counts[1:].items():
        if not (set(unique_line).issubset(main_line)
                or set(main_line).issubset(unique_line)):
        #    main_lines.append(unique_line)
        #else:
            branch_lines.append(unique_line)

    # For the main subplot, just exclude the branches
    trains_on_main = stations_in_each_trip[~stations_in_each_trip.isin(branch_lines)]
    df_for_main = df[df.Train.isin(trains_on_main.index)]
    # If there are branches, plot them in other subplots
    # TODO multiple branches = multiple subplots
    trains_on_branch = stations_in_each_trip[stations_in_each_trip.isin(branch_lines)]
    df_for_branch = df[df.Train.isin(trains_on_branch.index)]

    verbatim = [
     '大宮(埼玉)',
     'さいたま新都心',
     '浦和',
     '赤羽',
     '横浜',
     '戸塚',
     '大船',
     '藤沢',
     '辻堂',
     '茅ケ崎',
     '平塚',
     '大磯',
     '二宮',
     '国府津',
     '鴨宮',
     '小田原',
     '早川',
     '根府川',
     '真鶴',
     '湯河原',
     '熱海',
     '来宮',
     '伊豆多賀',
     '網代',
     '宇佐美',
     '伊東',
     '函南',
     '三島',
     '沼津',
     ]
    main_branch = [
     '尾久',
     '上野',
     '東京',
     '新橋',
     '品川',
     '川崎',
     ]
    branch = [
     '池袋',
     '新宿',
     '渋谷',
     '恵比寿',
     '大崎',
     '武蔵小杉',
     ]
    branched = {}
    for a, b in zip(main_branch, branch):
        branched[a] = a + '/' + b
        branched[b] = a + '/' + b
    combined = {x: x for x in verbatim}
    combined.update(branched)

    def g(df, combined):
        import numpy as np
        df['Station_sequence'] = np.nan
        def f(x):
            for idx, row in x.iterrows():
                station = row.Station
                seq = combined[station]
                df.loc[idx, 'Station_sequence'] = seq
        df.groupby('Train').apply(f)

    plt_func = plotter.value[0]
    plt_func(
        df_for_main, df_for_branch,
        line.name, 'normal', alpha=0.5, color=line.color, line=True
    )

    # If only normal was missing, exit now
    if delta.exists() and delta_scatter.exists():
        return
    df_for_main = prepare_plot.prepare_delta(df_for_main)
    df_for_branch = prepare_plot.prepare_delta(df_for_branch)

    g(df_for_main, combined)
    g(df_for_branch, combined)

    plt_func(
        df_for_main, df_for_branch,
        line.name, 'delta', alpha=0.2, color=line.color, line=True
    )
    plt_func(
        df_for_main, df_for_branch,
        line.name, 'delta_scatter', alpha=0.2, color=line.color, line=False
    )


if __name__ == '__main__':
    chuo = Line(
        name = 'chuo',
        color = '#FE642E',
        url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    )
    chuo_sobu = Line(
        name = 'chuo_sobu',
        color = '#fdbc00',
        url = 'https://ekitan.com/timetable/railway/line-station/184-20/d2?dt=20211101'
    )
    kt = Line(
        name = 'keihin_tohoku',
        color = '#00BFFF',
        url = 'https://ekitan.com/timetable/railway/line-station/79-0/d1?dt=20211101'
    )
    yamanote = Line(
        name = 'yamanote',
        color = '#9acd32',
        url = 'https://ekitan.com/timetable/railway/line-station/182-15/d1?dt=20211101'
    )
    takasaki = Line(
        name = 'takasaki',
        color = '#FF8C00',
        url = 'https://ekitan.com/timetable/railway/line-station/136-4/d1?dt=20211101'
    )
    main(takasaki, plotter=Plotter.matplotlib)
