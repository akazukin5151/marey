import time
from pathlib import Path
from common import mkdirs_touch_open, fetch_soup

def main(line_name):
    print('Downloading urls online...')
    with open(f'out/urls/{line_name}.txt', 'r') as f:
        file_ = f.read()

    for line in file_.split('\n'):
        if line == '':
            continue
        url, file_name = line.split(';')
        file_name = Path(file_name)
        if file_name.exists():
            continue
        print(f'Preparing to fetch {url=}')
        print('Sleeping first...')
        time.sleep(2)
        page = fetch_soup(url)
        print(f'Fetch successful, writing to {file_name}')
        mkdirs_touch_open(str(page), file_name)
    else:
        print('No files downloaded because all outputs already exists')
