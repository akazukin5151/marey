from .common import Constants
from marey.lib import save_page

def main(url, line_name):
    outfile = Constants.html_dir / f'{line_name}.html'
    return save_page.main(url, line_name, outfile)
