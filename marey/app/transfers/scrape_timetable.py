from pathlib import Path
from marey.lib import save_page
from marey.lib import get_urls

'''(target_url, train_dep_hour, train_dep_min, train_dest, train_speed)'''
TimetableData = tuple[str, str, str, str, str]

def scrape_timetable_urls(line_name: str, timetable_url: str) -> list[TimetableData]:
    # download timetable url to html
    timetable_html_path = Path('out/transfers/line') / f'{line_name}.html'
    save_page.main(timetable_url, timetable_html_path)

    # scrape urls from html
    return get_urls.main(timetable_html_path)


def find_train_in_timetable_data(rs: list[TimetableData], time: str) -> tuple[int, str]:
    # find train that matches `time` and return url
    splitted = time.split(':')
    hour = splitted[0]
    minute = splitted[1]
    for idx, (target_url, train_dep_hour, train_dep_min, _, _) in enumerate(rs):
        if train_dep_hour == hour and train_dep_min == minute:
            break
    else:  # no break
        raise Exception(f"couldn't find matching train at {time}")

    return (idx, target_url)
