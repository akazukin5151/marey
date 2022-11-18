from pathlib import Path
from bs4 import BeautifulSoup
from .common import mkdirs_touch_open, Constants

def main(html_path: Path, url_file: Path, url_dir: Path):
    if url_file.exists():
        return

    with open(html_path, 'r') as f:
        page = BeautifulSoup(f.read(), features='html.parser')

    # If the page is on a station that is not the terminus, the page
    # will contain 2 `ek-hour-line`s. The one with the `active` is the correct one
    active = page.find_all('div', 'tab-content-inner active')
    assert len(active) == 1
    # the table containing all the trains departing, grouped by departure hour
    hours_lines = active[0].find_all('tr', class_='ek-hour_line')

    result = []
    for hour_line in hours_lines:
        train_dep_hour = hour_line.find('td').get_text()
        # all the trains departing this hour
        trains = hour_line.find_all('li', class_='ek-tooltip ek-narrow ek-train-tooltip')
        for train in trains:
            train_dest = train.get('data-dest').replace('/', '_')
            train_speed = train.get('data-tr-type')
            train_dep_min = train.find('a').find('span', class_='time-min means-text')
            if train_dep_min is None:
                train_dep_min = train.find('a').find(
                    'span', class_='time-min means-text start'
                )
            train_dep_min = train_dep_min.get_text()
            target_url = get_target_url(train.find('a'))

            outname = url_dir / f'{train_dep_hour}-{train_dep_min}-{train_dest}-{train_speed}'
            out = f'{target_url};{outname}'
            result.append(out)

    mkdirs_touch_open('\n'.join(result), url_file)

def get_target_url(link):
    return 'https://ekitan.com' + link.get('href')
