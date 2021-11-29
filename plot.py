from common import Constants

def matplotlib(
    df: 'pd.DataFrame', line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    from matplotlib.ticker import AutoMinorLocator
    from common import mkdirs_touch_open

    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.png'
    if outfile.exists():
        return

    print(f'Plotting {plot_name} (offline)...')

    plt.rcParams['font.family'] = 'Hiragino Sans GB'
    plt.figure(figsize=(15, 15))

    args = dict(
        color=color,
        alpha=alpha,
        marker='o'
    )
    if not line:
        args.update(dict(linestyle='None'))  # Must be a string!

    # yikes
    for train in df.Train.unique():
        plt.plot(
            df[df.Train == train]['Arrive'],
            df[df.Train == train]['Station'],
            **args
        )
    plt.grid(which='both', alpha=0.7)
    plt.gca().tick_params(axis='x', which='minor')
    plt.gca().invert_yaxis()
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
    plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plt.gca().xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    plt.gca().xaxis.set_tick_params(labeltop='on')
    plt.gca().yaxis.set_tick_params(labelright='on')
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

