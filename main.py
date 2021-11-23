import get_urls
import download
import scrap_html
import prepare_plot
import plot

def main(url, line_name):
    get_urls.main(url, line_name)
    download.main(line_name)
    scrap_html.main(line_name)
    # This is not saved to a file because dtype data has to be preserved
    # You could still pickle it if you really want to export the entire thing intact
    df = prepare_plot.prepare_normal(line_name)
    plot.main(line_name, 'normal', df, 0.5)
    prepare_plot.prepare_delta(df)
    plot.main(line_name, 'delta', df, 0.2)


if __name__ == '__main__':
    # don't use "current" results, always pin to a specific date
    # NO: 'https://ekitan.com/timetable/railway/line-station/180-0/d1'
    url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    line_name = 'chuo'
    main(url, line_name)
