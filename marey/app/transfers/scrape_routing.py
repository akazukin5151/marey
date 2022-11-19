from typing import List, Tuple, Any
from pathlib import Path
from .common import Route
from marey.lib.get_urls import get_target_url
from bs4 import BeautifulSoup

'''Type alias of a BeautifulSoup object, which doesn't have stubs'''
Soup = Any

Name = str
Time = str
Url = str
StationData = Tuple[Name, Time, Url]

CssClass = str

def scrape_html(route: Route) -> Tuple[List[StationData], Name, Url, List[CssClass]]:
    filename = Path('out/transfers/routing') / f'{route.filename}.html'
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read(), features='html.parser')

    results = soup.find_all('div', class_='ek-page-no-1')
    result: Soup = results[route.result_idx]

    starting_station_data = parse_starting_station(result, route.date)
    transfer_stations_data = parse_transfer_stations(result, route.date)
    all_stations_data = [starting_station_data] + transfer_stations_data

    dest_station = parse_dest_station_name(result)

    stylesheet_url = get_stylesheet_url(soup)

    colors_soups = result.find_all('td', class_='td-line-color')
    color_classes = [colors_soup['class'][2] for colors_soup in colors_soups]

    return (all_stations_data, dest_station, stylesheet_url, color_classes)

def get_stylesheet_url(s: Soup) -> Url:
    return get_target_url(s.find('link', rel='stylesheet'))

def parse_starting_station(result: Soup, date: str) -> StationData:
    starting_station = result.find('div', class_='result-route-departure-wrap')
    return parse_station(starting_station, date)

def parse_dest_station_name(result: Soup) -> Name:
    dest_station = result.find('div', class_='result-route-arrival-wrap')
    return get_station_name(dest_station)

def parse_transfer_stations(result: Soup, date: str) -> List[StationData]:
    transfer_stations = result.find_all(
        'div', class_='result-route-transfer-sta-wrap'
    )
    return [
        parse_transfer_station(transfer_station, date)
        for transfer_station in transfer_stations
    ]

def parse_transfer_station(transfer_station: Soup, date: str) -> StationData:
    (name, time, timetable_url) = parse_station(transfer_station, date)
    time = time.replace('発', '')
    return (name, time, timetable_url)

def parse_station(station: Soup, date: str) -> StationData:
    name = get_station_name(station)
    time = get_station_time(station)
    timetable_url = get_timetable_url(station, date)
    return (name, time, timetable_url)

def get_station_name(s: Soup) -> Name:
    return s.find('div', class_='name').get_text()

def get_station_time(s: Soup) -> Time:
    return s.find('div', class_='departure-time').get_text()

def get_timetable_url(s: Soup, date: str) -> Url:
    url = s.find(
        'div', class_='btn-group-simple-links'
    ).find('a').get('href')
    return url.replace('?dw=1', '') + '?' + date

