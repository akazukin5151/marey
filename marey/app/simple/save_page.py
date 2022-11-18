from .common import Constants
from marey.lib import save_page

def main(url, line_name):
    '''download a page showing the timetable of a station'''
    outfile = Constants.html_dir / f'{line_name}.html'
    return save_page.main(url, outfile)
