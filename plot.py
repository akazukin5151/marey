from common import Constants
from matplotlib import ticker

def matplotlib(
    df: 'DataFrame', df_for_branch: 'DataFrame',
    line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    from matplotlib.ticker import AutoMinorLocator
    from matplotlib.category import StrCategoryLocator, StrCategoryFormatter
    from common import mkdirs_touch_open
    from collections import OrderedDict

    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.png'
    if outfile.exists():
        return

    print(f'Plotting {plot_name} (offline)...')

    plt.rcParams['font.family'] = 'Hiragino Sans GB'
    _, ax = plt.subplots(figsize=(15, 15))

    args = dict(
        color=color,
        alpha=alpha,
        marker='o'
    )
    if not line:
        args.update(dict(linestyle='None'))  # Must be a string!

    # yikes
    for train in df.Train.unique():
        ax.plot(
            df[df.Train == train]['Arrive'],
            df[df.Train == train]['Station_sequence'],
            **args
        )

    branch_color = 'tab:blue'
    args['color'] = branch_color
    for train in df_for_branch.Train.unique():
        ax.plot(
            df_for_branch[df_for_branch.Train == train]['Arrive'],
            df_for_branch[df_for_branch.Train == train]['Station_sequence'],
            **args
        )

    ax.grid(which='both', alpha=0.7)
    ax.tick_params(axis='x', which='minor')
    ax.invert_yaxis()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    ax.xaxis.set_tick_params(labeltop='on')
    ax.yaxis.set_tick_params(labelright='on')

    plt.tight_layout()
    mkdirs_touch_open('', outfile)
    plt.savefig(outfile)

def bokeh(
    df: 'pd.DataFrame', line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    import numpy as np
    from bokeh.plotting import figure, ColumnDataSource, save
    from bokeh.io import output_file

    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.html'
    if outfile.exists():
        return

    print(f'Plotting {plot_name} (offline)...')
    output_file(outfile)

    source = ColumnDataSource(data=df)
    p1 = figure(
        x_axis_type='datetime', y_range=np.flip(df.Station.unique()),
        tools='hover,pan,wheel_zoom,box_zoom,reset',
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "($x, $y)"),
            ("Train", "@Train"),
        ]
    )
    p1.circle('Arrive', 'Station', source=source, alpha=alpha, color=color)
    if line:
        p1.line('Arrive', 'Station', source=source, alpha=alpha, color=color)
    save(p1)

def altair(
    df: 'pd.DataFrame', line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    import altair as alt

    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.html'
    if outfile.exists():
        return

    print(f'Plotting {plot_name} (offline)...')

    if line:
        begin = alt.Chart(df).mark_line(
            order=False, point=alt.OverlayMarkDef(color=color), opacity=alpha, color=color
        )
    else:
        begin = alt.Chart(df).mark_circle(order=False, fillOpacity=alpha, color=color)

    selection = alt.selection_interval(bind='scales', zoom=True)

    chart = begin.encode(
        x='Arrive',
        y=alt.Y('Station:O', sort=None),
        detail=alt.Detail('Train'),
        tooltip=['Train', 'Arrive', 'Station']
    ).add_selection(
        selection
    ).properties(
        width=900
    ).interactive(
        bind_x=True,
        bind_y=True
    )

    with open(outfile, 'w') as f:
        chart.save(f, 'html')

