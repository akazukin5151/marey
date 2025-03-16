from typing import List, Optional, Tuple, Any
from pathlib import Path
from .common import Route, CssClass
from marey.lib import save_page
from marey.lib.get_urls import get_target_url
from marey.lib import get_urls
from marey.lib.scrap_html import get_rest_station_info
from . import scrape_timetable
from bs4 import BeautifulSoup

'''Type alias of a BeautifulSoup object, which doesn't have stubs'''
Soup = Any

Name = str
Time = str
Url = str
StationData = Tuple[Name, Time, Optional[Url]]

def scrape_html(route: Route) -> Tuple[
    List[StationData], Name, Url, List[CssClass], List[str]
]:
    filename = Path('out/transfers/routing') / f'{route.filename}.html'
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    results = soup.find_all('div', class_='ek-page-no-1')
    result: Soup = results[route.result_idx]

    starting_station_data = parse_starting_station(result, route.date())
    transfer_stations_data = parse_transfer_stations(result, route.date())
    all_stations_data = [starting_station_data] + transfer_stations_data

    dest_station = parse_dest_station_name(result)

    stylesheet_url = get_stylesheet_url(soup)

    colors_soups = result.find_all('td', class_='td-line-color')
    color_classes = [colors_soup['class'][2] for colors_soup in colors_soups]

    # exclude the 'walking' transportation mode
    line_names = [ln for ln in parse_line_names(result) if ln != '徒歩']

    return (
        all_stations_data, dest_station, stylesheet_url, color_classes, line_names
    )

def parse_line_names(result: Soup) -> List[str]:
    line_names = []
    for soup in result.find_all('div', class_='transportation'):
        text = soup.find('span', class_='name').get_text()
        line_name = text.split(' ')[0]
        line_names.append(line_name)
    return line_names

def get_stylesheet_url(s: Soup) -> Url:
    return get_target_url(s.find('link', rel='stylesheet'))

def parse_starting_station(result: Soup, date: str) -> StationData:
    starting_station = result.find('div', class_='result-route-departure-wrap')
    return parse_station(starting_station, date, None, None)

def parse_dest_station_name(result: Soup) -> Name:
    dest_station = result.find('div', class_='result-route-arrival-wrap')
    return get_station_name(dest_station)

def parse_transfer_stations(result: Soup, date: str) -> List[StationData]:
    divs = result.find_all('div')
    res = []
    for div in divs:
        # also include stations between through services
        # as past/future times may not have the exact same through service
        # but the journey can still be continued by manually changing
        # at that station
        if (
            'result-route-transfer-sta-wrap' in div.get('class')
            or 'result-route-station-direct-wrap' in div.get('class')
        ):
            prev_time = None if len(res) == 0 else res[-1][1]
            prev_timetable_url = None if len(res) == 0 else res[-1][2]
            # this can be a through service station
            # if so, we need to get the prev transfer station (not through service)
            # and use its timetable to find the departure time at the through
            # service station.
            # TODO: prev non through service station
            r = parse_transfer_station(div, date, prev_timetable_url, prev_time)
            res.append(r)

    return res

def parse_transfer_station(
    transfer_station: Soup,
    date: str,
    prev_timetable_url: Optional[Url],
    prev_time: Optional[Time],
) -> StationData:
    (name, time, timetable_url) = parse_station(
        transfer_station, date, prev_timetable_url, prev_time
    )
    time = time.replace('発', '')
    return (name, time, timetable_url)

def parse_station(
    station: Soup,
    date: str,
    prev_timetable_url: Optional[Url],
    prev_time: Optional[Time],
) -> StationData:
    name_elem = station.find('div', class_='name')
    name = name_elem.get_text().strip()
    time = get_station_time(station, name, prev_timetable_url, prev_time)
    timetable_url = get_timetable_url(station, name_elem, name, date)
    return (name, time, timetable_url)

def get_station_name(s: Soup) -> Name:
    return s.find('div', class_='name').get_text().strip()

def get_station_time(
    s: Soup,
    name: Name,
    prev_timetable_url: Optional[Url],
    prev_time: Optional[Time],
) -> Time:
    elem = s.find('div', class_='departure-time')
    if elem is not None:
        return elem.get_text()

    if prev_timetable_url is None or prev_time is None:
        raise Exception('cannot find depature time and timetable url or prev time is none')

    # this station is a station that leads to through services.
    # no manual transfer is needed, but we still want to show this
    # as two separate lines as if a transfer has happened.
    # to do this, we need to get the departure time.
    # we can only do this by going to the previous transfer station's timetable,
    # find the matching train, get that train's station list, and get the
    # departure time in that station list.

    # download timetable url to html
    line_name = 'prev_' + name + '_part'
    timetable_data = scrape_timetable.scrape_timetable_urls(
        line_name, prev_timetable_url
    )
    _, target_url = scrape_timetable.find_train_in_timetable_data(
        timetable_data, prev_time
    )

    # download page of the train for this leg
    journey_html = Path('out/transfers/journey') / f'to {name} from {prev_time}.html'
    save_page.main(target_url, journey_html)

    # scrape the departure time for name (大和西大寺)
    dep_t = scrape_dep_time(journey_html, name)
    if dep_t is None:
        raise Exception('could not scrape depature time')

    return dep_t

def scrape_dep_time(file_: Path, name: Name) -> Optional[str]:
    print('Scraping html... (offline)')
    with open(file_, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    first_station = soup.find('div', class_='result-route-departure-wrap')
    rest_stations = soup.find_all('div', class_='result-route-transfer-wrap')
    all_stations = [first_station] + rest_stations

    for station in all_stations:
        (station_name, _, dep_t) = get_rest_station_info(station)
        if station_name == name:
            return dep_t

    return None

def get_timetable_url(s: Soup, name_elem: Soup, name: Name, date: str) -> Optional[Url]:
    links = s.find('div', class_='btn-group-simple-links')
    if links is not None:
        link = links.find('a')
        if link.get_text() == '時刻表':
            url = link.get('href')
            return url.replace('?dw=0', '') + '?dt=' + date

    station_link = name_elem.find('a').get('href')
    station_id = station_link.split('/')[-1]
    station_url = f'https://ekitan.com/timetable/railway/station/{station_id}'

    html_path = Path('out/transfers/station/' + name + '.html')

    # parse what train and direction the route is telling us to go
    matched = get_match_info(s)
    if matched is None:
        return None

    line_name_to_match, direction_to_match = matched

    # download the station page with a list of all lines serving the station
    save_page.main(station_url, html_path)

    with open(html_path, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    # find service that matches our route
    url = find_matching_service(soup, line_name_to_match, direction_to_match)

    return url + '?dt=' + date

def get_match_info(s: Soup) -> Optional[Tuple[str, str]]:
    section = s.find_next_sibling('div')
    transportation = section.find('div', class_='transportation')
    walk = transportation.find('span', 'feis-walk')
    if walk is not None:
        return None

    text = transportation.find('span', class_='name').get_text()
    splitted = text.split(' ')
    line_name = splitted[0]
    direction_name = splitted[2][:-2]
    return line_name, direction_name

def find_matching_service(
    soup: Soup, line_name_to_match: str, direction_to_match: str
) -> Url:
    services = soup.find_all('div', class_='link-wrap type04')
    for service in services:
        dls = service.find_all('dl')
        for dl in dls:
            line_name = dl.find('dt').find('span').find('a').get_text()
            if line_name == line_name_to_match:
                directions = dl.find('dd').find('ul').find_all('li')
                direction_infos = []
                for direction in directions:
                    link = direction.find('a')
                    dir_name = link.get_text().replace('方面', '')
                    direction_infos.append((link, dir_name))
                    if dir_name == direction_to_match:
                        return get_target_url(link)
                # line found but direction not found: ask for correct direction
                return ask_direction(line_name_to_match, direction_to_match, direction_infos)
    return ask_timetable_url(line_name_to_match, direction_to_match)

def ask_direction(
    line_name_to_match: str, direction_to_match: str, direction_infos: list[str]
) -> Url:
    print(f'Found line {line_name_to_match}, but direction {direction_to_match} not found, please enter corresponding direction index')
    print('Found directions:')
    for idx, (_, dir_name) in enumerate(direction_infos):
        print(f'{idx}: {dir_name}')

    while True:
        input_ = input('index: ')
        try:
            chosen_idx = int(input_)
            break
        except Exception:
            print('could not parse int')

    link = direction_infos[chosen_idx][0]
    return get_target_url(link)

def ask_timetable_url(
    line_name_to_match: str, direction_to_match: str
) -> Url:
    print('Could not get timetable, please enter timetable url')
    print(f'{line_name_to_match=}')
    print(f'{direction_to_match=}')
    print('eg: https://ekitan.com/timetable/railway/line-station/182-9/d1?dt=20221119')
    return input('url: ')

