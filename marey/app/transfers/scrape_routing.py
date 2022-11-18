from typing import List, Tuple, Any
from pathlib import Path
from .common import Route
from bs4 import BeautifulSoup

'''Type alias of a BeautifulSoup object, which doesn't have stubs'''
Soup = Any

def scrape_html(route: Route) -> List[Tuple[str, str, str]]:
    filename = Path('out/transfers/routing') / f'{route.filename}.html'
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    results = soup.find_all('div', class_='ek-page-no-1')
    result: Soup = results[route.result_idx]

    starting_station_data = parse_starting_station(result, route.date)
    transfer_stations_data = parse_transfer_stations(result, route.date)
    all_stations_data = [starting_station_data] + transfer_stations_data
    return all_stations_data

def parse_starting_station(result: Soup, date: str) -> Tuple[str, str, str]:
    starting_station = result.find('div', class_='result-route-departure-wrap')
    return parse_station(starting_station, date)

def parse_transfer_stations(result: Soup, date: str) -> List[Tuple[str, str, str]]:
    transfer_stations = result.find_all(
        'div', class_='result-route-transfer-sta-wrap'
    )
    return [
        parse_transfer_station(transfer_station, date)
        for transfer_station in transfer_stations
    ]

def parse_transfer_station(transfer_station: Soup, date: str) -> Tuple[str, str, str]:
    (name, time, timetable_url) = parse_station(transfer_station, date)
    time = time.replace('発', '')
    return (name, time, timetable_url)

def parse_station(transfer_station: Soup, date: str) -> Tuple[str, str, str]:
    name = get_station_name(transfer_station)
    time = get_station_time(transfer_station)
    timetable_url = get_timetable_url(transfer_station, date)
    return (name, time, timetable_url)

def get_station_name(s: Soup) -> str:
    return s.find('div', class_='name').get_text()

def get_station_time(s: Soup) -> str:
    return s.find('div', class_='departure-time').get_text()

def get_timetable_url(s: Soup, date: str) -> str:
    url = s.find(
        'div', class_='btn-group-simple-links'
    ).find('a').get('href')
    return url.replace('?dw=1', '') + '?' + date

