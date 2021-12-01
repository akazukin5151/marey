from enum import Enum
from common import Constants, Line, BranchData
import save_page
import get_urls
import download
import scrap_html
import prepare_plot
import plot
import combined

# Only matplotlib supports the second DataFrame argument
# (DataFrame -> Maybe DataFrame -> str -> str -> float -> str -> bool -> IO (), str)
class Plotter(Enum):
    matplotlib = (plot.matplotlib, 'png')
    bokeh      = (plot.bokeh,      'html')
    altair     = (plot.altair,     'html')

def main(line: Line, plotter: Plotter):
    save_page.main(line.url, line.name)
    get_urls.main(line.url, line.name)
    download.main(line.name)
    scrap_html.main(line.name)

    # Check if plot needs to be prepared
    ext = plotter.value[1]
    normal = Constants.plot_dir / f'{line.name}_normal.{ext}'
    delta = Constants.plot_dir / f'{line.name}_delta.{ext}'
    delta_scatter = Constants.plot_dir / f'{line.name}_delta_scatter.{ext}'
    if normal.exists() and delta.exists() and delta_scatter.exists():
        return

    df = prepare_plot.prepare_normal(line.name)

    if line.branch_data is not None:
        df_for_main, df_for_branch = prepare_plot.handle_branches(df, line)
    else:
        df_for_main, df_for_branch = df, None

    plt_func = plotter.value[0]
    plt_func(
        df_for_main, df_for_branch,
        line.name, 'normal', alpha=0.5, color=line.color, line=True
    )

    # If only normal was missing, exit now
    if delta.exists() and delta_scatter.exists():
        return

    df_for_main = prepare_plot.prepare_delta(line.name + '_main', df_for_main)
    if line.branch_data:
        df_for_branch = prepare_plot.prepare_delta(line.name + '_branch', df_for_branch)

    plt_func(
        df_for_main, df_for_branch,
        line.name, 'delta', alpha=0.2, color=line.color, line=True
    )
    plt_func(
        df_for_main, df_for_branch,
        line.name, 'delta_scatter', alpha=0.2, color=line.color, line=False
    )


if __name__ == '__main__':
    chuo = Line(
        name = 'chuo',
        color = '#FE642E',
        url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101',
        branch_data = None
    )
    chuo_sobu = Line(
        name = 'chuo_sobu',
        color = '#fdbc00',
        url = 'https://ekitan.com/timetable/railway/line-station/184-20/d2?dt=20211101',
        branch_data = None
    )
    kt = Line(
        name = 'keihin_tohoku',
        color = '#00BFFF',
        url = 'https://ekitan.com/timetable/railway/line-station/79-0/d1?dt=20211101',
        branch_data = None
    )
    yamanote = Line(
        name = 'yamanote',
        color = '#9acd32',
        url = 'https://ekitan.com/timetable/railway/line-station/182-15/d1?dt=20211101',
        branch_data = None
    )
    ueno_tokyo = Line(
        name = 'ueno_tokyo',
        color = '#FF8C00',
        url = 'https://ekitan.com/timetable/railway/line-station/136-4/d1?dt=20211101',
        # I'm not sure where to scrap reliable data for this
        branch_data = BranchData(
            verbatim = [
                '大宮(埼玉)',
                'さいたま新都心',
                '浦和',
                '赤羽',
                '横浜',
                '戸塚',
                '大船',
                '藤沢',
                '辻堂',
                '茅ケ崎',
                '平塚',
                '大磯',
                '二宮',
                '国府津',
                '鴨宮',
                '小田原',
                '早川',
                '根府川',
                '真鶴',
                '湯河原',
                '熱海',
                '来宮',
                '伊豆多賀',
                '網代',
                '宇佐美',
                '伊東',
                '函南',
                '三島',
                '沼津',
            ],
            main_branch = [
                '尾久',
                '上野',
                '東京',
                '新橋',
                '品川',
                '川崎',
            ],
            branch = [
                '池袋',
                '新宿',
                '渋谷',
                '恵比寿',
                '大崎',
                '武蔵小杉',
            ]
        )
    )
    # Note that only matplotlib works with branches for now...
    main(ueno_tokyo, plotter=Plotter.matplotlib)
    fixes = [
        ('尾久', '上中里'),
        ('戸塚', '磯子')
    ]
    combined.delta(kt, ueno_tokyo, fixes)
    combined.delta_subsets(
        [kt, ueno_tokyo, yamanote],
        ['赤羽', '赤羽', None],
        [None, None, '大崎'],
        [(0, 2, '田端')],
        fixes
    )
    combined.delta_scatter(kt, ueno_tokyo, fixes)
    combined.delta_subsets_scatter(
        [kt, ueno_tokyo, yamanote],
        ['赤羽', '赤羽', None],
        [None, None, '大崎'],
        [(0, 2, '田端')],
        fixes
    )
