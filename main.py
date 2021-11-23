from pathlib import Path
import save_page
import get_urls
import download
import scrap_html
import prepare_plot
import plot

def main(url, line_name, line_color):
    save_page.main(url, line_name)
    get_urls.main(url, line_name)
    download.main(line_name)
    scrap_html.main(line_name)

    # Check if plot needs to be prepared
    normal = Path(f'plots/{line_name}_normal.png')
    delta = Path(f'plots/{line_name}_delta.png')
    delta_scatter = Path(f'plots/{line_name}_delta_scatter.png')
    if normal.exists() and delta.exists() and delta_scatter.exists():
        return

    df = prepare_plot.prepare_normal(line_name)
    plot.main(df, line_name, 'normal', alpha=0.5, color=line_color, line=True)

    # If only normal was missing, exit now
    if delta.exists() and delta_scatter.exists():
        return
    prepare_plot.prepare_delta(df)
    plot.main(df, line_name, 'delta', alpha=0.2, color=line_color, line=True)
    plot.main(df, line_name, 'delta_scatter', alpha=0.2, color=line_color, line=False)


if __name__ == '__main__':
    # don't use "current" results, always pin to a specific date
    # NO: 'https://ekitan.com/timetable/railway/line-station/180-0/d1'
    #line_name = 'chuo_sobu'
    #line_color = '#fdbc00'
    #url = 'https://ekitan.com/timetable/railway/line-station/184-20/d2?dt=20211101'
    line_name = 'chuo'
    line_color = '#FE642E'
    url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    main(url, line_name, line_color)
