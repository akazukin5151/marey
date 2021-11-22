import get_urls
import download
import scrap_html
import prepare_plot
import plot

def main(url, line_name):
    print('Getting urls...')
    get_urls.main(url, line_name)
    print('Downloading urls...')
    download.main(line_name)
    print('Scraping html... (offline)')
    scrap_html.main(line_name)
    # This is not saved to a file because dtype data has to be preserved
    # You could still pickle it if you really want to export the entire thing intact
    print('Preparing plot...')
    df = prepare_plot.main(line_name)
    print('Plotting...')
    plot.main(line_name, df)

if __name__ == '__main__':
    # don't use "current" results, always pin to a specific date
    # NO: 'https://ekitan.com/timetable/railway/line-station/180-0/d1'
    url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    line_name = 'chuo'
    main(url, line_name)
