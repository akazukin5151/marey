from pathlib import Path
from .common import Route
from marey.lib import save_page
from . import scrape_routing
from marey.lib import get_urls
from marey.lib import scrap_html
from marey.lib import prepare_plot
from marey.lib import plot

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

        # download that page
        journey_html = Path('out/transfers/journey') / f'{name}-{time}.html'
        save_page.main(target_url, journey_html)

        # scrape that html
        # TODO: change html_dir into an iterator of html files
        # so that every loop treats different lines separately
        # currently, every line is in the journey dir so every loop
        # will read every line html, so all the resulting csv are the same
        # and it treats the entire route on different lines as the same "line"
        scrap_html.main(
            Path('out/transfers/journey'),
            Path('out/transfers/generated_csv') / (line_name + '.csv')
        )

    # using new code, remove stations outside origin and destination
    # (outside specific time sections)

    # using pre-existing code, plot the result
    #plot_dir = Path('out/transfers/plot')
    #normal = plot_dir / f'{line_name}_normal.png'
    #if normal.exists():
    #    return
    # TODO: different input file
    #df = prepare_plot.prepare_normal(line_name)
    #plt_func = plot.matplotlib
    # TODO: different output file
    #plt_func(
    #    df, None,
    #    line_name, 'normal', alpha=0.5, color='red', line=True
    #)


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
