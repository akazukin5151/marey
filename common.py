from typing import NamedTuple
from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup

class Constants(NamedTuple):
    url_dir:     Path = Path('out/urls')
    html_dir:    Path = Path('out/htmls')
    gen_csv_dir: Path = Path('out/generated_csv')
    plot_dir:    Path = Path('out/plots')

class Line(NamedTuple):
    name:  str
    color: str
    url:   str

def mkdirs_touch_open(s: str, path: Path):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.touch(exist_ok=True)
    with open(path, 'w') as f:
        f.write(s)

def fetch_soup(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    return BeautifulSoup(html, "html.parser")
