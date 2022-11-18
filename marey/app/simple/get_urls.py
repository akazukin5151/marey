from marey.lib import get_urls
from .common import Constants, mkdirs_touch_open

def main(line_name):
    url_file = Constants.url_dir / f'{line_name}.txt'
    url_dir = Constants.html_dir / line_name
    if url_file.exists():
        return

    rs = get_urls.main(
        html_path=Constants.html_dir / f'{line_name}.html',
    )

    result = []
    for (target_url, train_dep_hour, train_dep_min, train_dest, train_speed) in rs:
        outname = url_dir / f'{train_dep_hour}-{train_dep_min}-{train_dest}-{train_speed}'
        out = f'{target_url};{outname}'
        result.append(out)
    mkdirs_touch_open('\n'.join(result), url_file)
