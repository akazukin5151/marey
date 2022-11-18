from marey.lib import get_urls
from .common import Constants

def main(line_name):
    return get_urls.main(
        html_path=Constants.html_dir / f'{line_name}.html',
        url_file=Constants.url_dir / f'{line_name}.txt',
        url_dir=Constants.html_dir / line_name
    )
