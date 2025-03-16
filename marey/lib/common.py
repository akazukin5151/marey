from typing import NamedTuple
from time import sleep
from datetime import date
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup

class Constants(NamedTuple):
    url_dir     = Path('out/urls')
    html_dir    = Path('out/htmls')
    gen_csv_dir = Path('out/generated_csv')
    plot_dir    = Path('out/plots')
    today       = date.today()
    midnight    = datetime.combine(today, datetime.min.time())

class Line(NamedTuple):
    name:     str
    color:    str
    url:      str
    branch_data: 'Optional[List[(str, str)]]'

def mkdirs_touch_open(s: str, path: Path):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.touch(exist_ok=True)
    with open(path, 'w') as f:
        f.write(s)

def fetch_soup(url):
    n_tries = 0
    while True:
        if n_tries > 0:
            sleep(2 ** n_tries)
        if n_tries >= 5:
            raise Exception('failed to fetch')
        try:
            page = urlopen(url)
            break
        except URLError:
            n_tries += 1

    html = page.read().decode("utf-8")
    return BeautifulSoup(html, "html.parser")
