from .common import Route
from . import save_page
from . import scrape_routing

def main(route: Route):
    save_page.main(route.to_url(), route.filename)
    all_stations_data = scrape_routing.scrape_html(route)

    print(all_stations_data)
    for (name, time, timetable_url) in all_stations_data:
        line_name = name + '_part'
        # using pre-existing code, download url to html
        # TODO: different output dir
        #save_page.main(timetable_url, line_name)

        # using pre-existing code, scrape urls from html
        # TODO: different input and output paths
        #get_urls.main(timetable_url, line_name)

        # using new code, find train that matches `time` and return url
        # url = TODO

        # using pre-existing code, download that page
        # this function only reads urls from a txt file, so write url to that file
        # with open(TODO, 'w') as f:
        #     f.write(url)
        # TODO: different input dir
        #download.main(line_name)

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
