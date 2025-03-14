from pathlib import Path
from .common import Route
from marey.lib import save_page
from . import scrape_routing
from . import scrape_css
from marey.lib import get_urls
from marey.lib import scrap_html
from . import combined
from marey.lib import prepare_plot
from . import plot

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

    # for every leg of the journey... (the route is made of legs and transfers)
    dfs = []
    for (name, time, timetable_url) in all_stations_data:
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

        # download page of the train for this leg
        journey_html = Path('out/transfers/journey') / f'{name}-{time}.html'
        save_page.main(target_url, journey_html)

        # scrape html of train for this leg
        csv_path = Path('out/transfers/generated_csv') / (line_name + '.csv')
        scrap_html.main([journey_html], csv_path)

        # prepare for plot (split up arrive and depart time into separate rows)
        if plot_out_path.exists():
            continue

        processed_csv_path = csv_path.with_stem(line_name + '_processed')
        df = prepare_plot.prepare_normal(
            in_csv=csv_path,
            out_csv=processed_csv_path
        ).reset_index()
        dfs.append(df)

    # remove stations outside origin and destination
    names_to_remove = [name for (name, _, _) in all_stations_data[1:]]
    names_to_remove.append(dest_station)
    for df, name in zip(dfs, names_to_remove):
        combined.remove_stations_after_exclusive(name, df)

    # plot the entire route
    plot.main(dfs, plot_out_path, colors, line_names)


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
