import time
from pathlib import Path
from bs4 import BeautifulSoup
from common import mkdirs_touch_open, fetch_soup

def main(URL, line_name):
    if Path(f'out/urls/{line_name}.txt').exists():
        return

    with open(f'out/htmls/{line_name}.html', 'r') as f:
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
            target_url = get_target_url(URL, train.find('a'))

            out = f'{target_url};out/htmls/{line_name}/{train_dep_hour}-{train_dep_min}-{train_dest}-{train_speed}'
            result.append(out)

    mkdirs_touch_open('\n'.join(result), Path(f'out/urls/{line_name}.txt'))

def get_target_url(URL, link):
    # {{{ JS function for reference
    """
    $('.ek-train-link').on("click", function(){
        var $self = $(this);

        if($self.hasClass('ek-not-click') == true) {
            return false;
        }

        var sf = $self.data('sf');
        var tx = $self.data('tx');

        // var SF = $('[data-ek-code]').data('ek-code');

        if(tx == '') {
            return false;
        }

        var dw = '';
        $('.ek-dw-select').each(function(){
            if($(this).hasClass('active')) {
                dw = $(this).data('dw');
            }
        });

        var dt = '';
        if(dw != '0' && dw != '1' && dw != '2') {
            dt = $('.ek-year').children('option:selected').val() + $('.ek-month').children('option:selected').val() + $('.ek-day').children('option:selected').val();
        }

        var departure = $self.data('departure');
        var d = getSelectedDirection();

        var url = '/timetable/railway/train?sf=' + sf + '&tx=' + tx + '&dw=' + dw + '&dt=' + dt + '&departure=' + departure
         + '&SFF=180-0' + '&d=' + d;
        location.href = url;
        return false;
    """
    # }}}
    sf = link.get('data-sf')
    tx = link.get('data-tx')
    # unknown when this fills
    dw = ''

    # the date range of the current search
    dt = URL.split('?dt=')[-1]

    departure = link.get('data-departure')

    # hardcoded - my current search is outbound
    d = '1'

    # This is probably the line-station code in the url
    sff = '&SFF=180-0'

    return 'https://ekitan.com/timetable/railway/train?sf=' + sf + '&tx=' + tx + '&dw=' + dw + '&dt=' + dt + '&departure=' + departure + sff + '&d=' + d
