from typing import NamedTuple
from datetime import date
from datetime import datetime
from pathlib import Path

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
