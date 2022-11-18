from .common import mkdirs_touch_open, fetch_soup

def main(url, outfile):
    if outfile.exists():
        return
    print('Getting urls online...')

    print('Fetching the page...')
    page = fetch_soup(url)
    print('Page fetched!')
    mkdirs_touch_open(str(page), outfile)

