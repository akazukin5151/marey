from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup

def mkdirs_touch_open(s: str, path: Path):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.touch(exist_ok=True)
    with open(path, 'w') as f:
        f.write(s)

def fetch_soup(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    return BeautifulSoup(html, "html.parser")
