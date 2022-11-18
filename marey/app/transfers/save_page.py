from pathlib import Path
from marey.lib import save_page

def main(url, line_name):
    outfile = Path('out/transfers/routing') / f'{line_name}.html'
    return save_page.main(url, line_name, outfile)

