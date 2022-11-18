from pathlib import Path
from .common import Route
from marey.lib import save_page
from . import scrape_routing
from marey.lib import get_urls

def main(route: Route):
    outfile = Path('out/transfers/routing') / f'{route.filename}.html'
    save_page.main(route.to_url(), outfile)
    all_stations_data = scrape_routing.scrape_html(route)

    print(all_stations_data)
    for (name, time, timetable_url) in all_stations_data:
        line_name = name + '_part'

        # download timetable url to html
        outfile = Path('out/transfers/line') / f'{line_name}.html'
        save_page.main(timetable_url, outfile)

        # scrape urls from html
        rs = get_urls.main(outfile)

        # find train that matches `time` and return url
        splitted = time.split(':')
        hour = splitted[0]
        minute = splitted[1]
        for (target_url, train_dep_hour, train_dep_min, _, _) in rs:
            if train_dep_hour == hour and train_dep_min == minute:
                break
        else:  # no break
            raise Exception(f"couldn't find matching train at {time}")
        print(target_url)

        # using pre-existing code, download that page
        #save_page.main(url, line_name, TODO)

        # using pre-existing code, scrape that html
        # TODO: different input dir
        #scrap_html.main(line_name)
        pass

    # using new code, remove stations outside origin and destination
    # (outside specific time sections)
    # using pre-existing code, plot the result


if __name__ == '__main__':
    route = Route(
        date='20221119',
        time='1000',
        start='ueno',
        end='futako-tamagawa',
        filename='ueno-futako-tamagawa',
        result_idx=0
    )
    main(route)
