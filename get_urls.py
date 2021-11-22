import time
from pathlib import Path
from common import mkdirs_touch_open, fetch_soup

def main(URL, line_name):
    if Path(f'urls/{line_name}.txt').exists():
        return
    print('Getting urls...')

    print('Fetching the page...')
    # a page showing the timetable of a station
    page = fetch_soup(URL)
    print('Page fetched!')

    # the table containing all the trains departing, grouped by departure hour
    hours_lines = page.find_all('tr', class_='ek-hour_line')

    result = []
    for hour_line in hours_lines:
        train_dep_hour = hour_line.find('td').get_text()
        # all the trains departing this hour
        trains = hour_line.find_all('li', class_='ek-tooltip ek-narrow ek-train-tooltip')
        for train in trains:
            train_dest = train.get('data-dest').replace('/', '_')
            train_speed = train.get('data-tr-type')
            train_dep_min = train.find('a').find('span', class_='time-min means-text start').get_text()
            target_url = get_target_url(train.find('a'))

            out = f'{target_url};htmls/{line_name}/{train_dep_hour}-{train_dep_min}-{train_dest}-{train_speed}'
            result.append(out)

    mkdirs_touch_open('\n'.join(result), Path(f'urls/{line_name}.txt'))

def get_target_url(link):
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

    # hardcoded - the date range of my current search
    dt = '20211122'

    departure = link.get('data-departure')

    # hardcoded - my current search is outbound
    d = '1'

    # This is probably the line-station code in the url
    sff = '&SFF=180-0'

    return 'https://ekitan.com/timetable/railway/train?sf=' + sf + '&tx=' + tx + '&dw=' + dw + '&dt=' + dt + '&departure=' + departure + sff + '&d=' + d

if __name__ == '__main__':
    URL = "https://ekitan.com/timetable/railway/line-station/180-0/d1"
    line_name = 'chuo'
    main(URL, line_name)
