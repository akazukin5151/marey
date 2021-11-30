from typing import NamedTuple
from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup

class Constants(NamedTuple):
    url_dir     = Path('out/urls')
    html_dir    = Path('out/htmls')
    gen_csv_dir = Path('out/generated_csv')
    plot_dir    = Path('out/plots')

class Line(NamedTuple):
    name:     str
    color:    str
    url:      str
    branched: 'Optional[BranchData]'

class BranchData(NamedTuple):
    """
    This only supports branches that split up from the main line but merge back again
    Also only works if `len(main_branch) == len(branch)`

    A -> B ->  C -> D -> G -> H
           \_> E -> F /

    verbatim = [A, B, G, H], main_branch = [C, D], and branch = [E, F]
    """
    verbatim:    'List[str]'
    main_branch: 'List[str]'
    branch:      'List[str]'

def mkdirs_touch_open(s: str, path: Path):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.touch(exist_ok=True)
    with open(path, 'w') as f:
        f.write(s)

def fetch_soup(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    return BeautifulSoup(html, "html.parser")
