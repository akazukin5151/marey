from pathlib import Path
from typing import Optional
from .common import Route
from marey.lib import save_page
from . import scrape_routing
from . import scrape_css
from marey.lib import get_urls
from marey.lib import scrap_html
from . import combined
from marey.lib import prepare_plot
from . import plot

from .scrape_routing import StationData
import pandas as pd

def main(route: Route):
    route_html_path = Path('out/transfers/routing') / f'{route.filename}.html'
    plot_dir = Path('out/transfers/plot')
    plot_out_path = plot_dir / f'{route.filename}.png'

    # search the route on ekitan and save the result html
    save_page.main(route.url, route_html_path)

    # scrape the route html
    (
        all_stations_data,
        dest_station,
        stylesheet_url,
        color_classes,
        line_names
    ) = scrape_routing.scrape_html(route)

    # download the stylesheet
    stylesheet_path = Path('out/transfers/stylesheet.css')
    save_page.main(stylesheet_url, stylesheet_path)

    # get the colors
    colors = scrape_css.main(stylesheet_path, color_classes)

    # eg:
    # names_to_remove = [s1, s3, s6]
    # for the first line [s1, s2, s3, s4], remove everything after s3.
    # for the second line, remove everything after s6.
    names_to_remove = [name for (name, _, _) in all_stations_data[1:]]
    names_to_remove.append(dest_station)

    # the route is made of legs and transfers
    # for every leg of the journey, scrape the leg
    dfs = []
    for station_data, to_remove in zip(all_stations_data, names_to_remove):
        df = scrape_leg(station_data, to_remove, plot_out_path)
        if df is not None:
            dfs.append(df)

    # plot the entire route
    plot.main(dfs, plot_out_path, colors, line_names)

def scrape_leg(
    station_data: StationData,
    to_remove: str,
    plot_out_path: Path
) -> Optional[pd.DataFrame]:
    name = station_data[0]
    time = station_data[1]
    timetable_url = station_data[2]

    if timetable_url is None:
        return None

    line_name = name + '_part'

    # download timetable url to html
    timetable_html_path = Path('out/transfers/line') / f'{line_name}.html'
    save_page.main(timetable_url, timetable_html_path)

    # scrape urls from html
    rs = get_urls.main(timetable_html_path)

    # find train that matches `time` and return url
    splitted = time.split(':')
    hour = splitted[0]
    minute = splitted[1]
    for (target_url, train_dep_hour, train_dep_min, _, _) in rs:
        if train_dep_hour == hour and train_dep_min == minute:
            break
    else:  # no break
        raise Exception(f"couldn't find matching train at {time}")

    return scrape_train(
        name, time, line_name, plot_out_path, to_remove, target_url
    )

def scrape_train(
    name: str,
    time: str,
    line_name: str,
    plot_out_path: Path,
    to_remove: str,
    target_url: str,
) -> Optional[pd.DataFrame]:
    '''scrape a train that has a specific time'''
    # download page of the train for this leg
    journey_html = Path('out/transfers/journey') / f'{name}-{time}.html'
    save_page.main(target_url, journey_html)

    # scrape html of train for this leg
    csv_path = Path('out/transfers/generated_csv') / (line_name + '.csv')
    scrap_html.main([journey_html], csv_path)

    # prepare for plot (split up arrive and depart time into separate rows)
    if plot_out_path.exists():
        return None

    processed_csv_path = csv_path.with_stem(line_name + '_processed')
    df = prepare_plot.prepare_normal(
        in_csv=csv_path,
        out_csv=processed_csv_path
    ).reset_index()

    # remove stations outside origin and destination
    combined.remove_stations_after_exclusive(to_remove, df)

    return df


if __name__ == '__main__':
    main(Route(
        url='https://ekitan.com/transit/route/sf-1627/st-2962?sfname=%E4%B8%8A%E9%87%8E&stname=%E4%BA%8C%E5%AD%90%E7%8E%89%E5%B7%9D&dt=20250314&tm=1000',
        filename='上野→二子玉川',
        result_idx=0
    ))

    main(Route(
        url='https://ekitan.com/transit/route/sf-2489/st-1483?sfname=%E7%94%B0%E7%84%A1&stname=%E7%A7%8B%E8%91%89%E5%8E%9F&dt=20250314&tm=1000',
        filename='田無→秋葉原',
        result_idx=0,
    ))
