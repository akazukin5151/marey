from pathlib import Path
from common import Constants, Line
import save_page
import get_urls
import download
import scrap_html
import prepare_plot
import plot

def main(line: Line):
    save_page.main(line.url, line.name)
    get_urls.main(line.url, line.name)
    download.main(line.name)
    scrap_html.main(line.name)

    # Check if plot needs to be prepared
    normal = Constants.plot_dir / f'{line.name}_normal.png'
    delta = Constants.plot_dir / f'{line.name}_delta.png'
    delta_scatter = Constants.plot_dir / f'{line.name}_delta_scatter.png'
    if normal.exists() and delta.exists() and delta_scatter.exists():
        return

    df = prepare_plot.prepare_normal(line.name)
    plot.main(df, line.name, 'normal', alpha=0.5, color=line_color, line=True)

    # If only normal was missing, exit now
    if delta.exists() and delta_scatter.exists():
        return
    prepare_plot.prepare_delta(df)
    plot.main(df, line.name, 'delta', alpha=0.2, color=line_color, line=True)
    plot.main(df, line.name, 'delta_scatter', alpha=0.2, color=line_color, line=False)


if __name__ == '__main__':
    chuo = Line(
        name = 'chuo',
        color = '#FE642E',
        url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    )
    chuo_sobu = Line(
        name = 'chuo_sobu',
        color = '#fdbc00',
        url = 'https://ekitan.com/timetable/railway/line-station/184-20/d2?dt=20211101'
    )
    kt = Line(
        name = 'keihin_tohoku',
        color = '#00BFFF',
        url = 'https://ekitan.com/timetable/railway/line-station/79-0/d1?dt=20211101'
    )
    main(kt)
