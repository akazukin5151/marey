from .common import Constants
from marey.lib import scrap_html

def main(line_name):
    return scrap_html.main(
        htmls=(Constants.html_dir / line_name).iterdir(),
        out_csv=Constants.gen_csv_dir / f'{line_name}.csv'
    )
