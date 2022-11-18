# TODO: duplicated code
# only change is outfile
from pathlib import Path
from marey.lib.common import mkdirs_touch_open, fetch_soup

def main(url, line_name):
    outfile = Path('out/transfers/routing') / f'{line_name}.html'
    if outfile.exists():
        return
    print('Getting urls online...')

    print('Fetching the page...')
    # a page showing the timetable of a station
    page = fetch_soup(url)
    print('Page fetched!')
    mkdirs_touch_open(str(page), outfile)

