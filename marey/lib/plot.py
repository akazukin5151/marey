from .common import Constants
import pandas as pd
import matplotlib.pyplot as plt


def core(outfile, plot_func, plot_format, plot_name, figsize):
    from .common import mkdirs_touch_open

    if outfile.exists():
        return

    print(f'Plotting {plot_name} (offline)...')

    plt.rcParams['font.family'] = 'Hiragino Sans GB'
    plt.figure(figsize=figsize)

    plot_func()
    plot_format()

    mkdirs_touch_open('', outfile)
    plt.savefig(outfile)
    plt.close()

def format_int_time(tick_value: int, pos: int) -> str:
    '''
    tick_value: int
        The arrival time, after conversion to int and divided by 1e12
    pos: int
        The index of the tick
    '''
    dt = pd.to_datetime(tick_value * 1e12)
    # {x : 03} means pad the string with zeros to ensure it is two digits
    return f"{dt.hour}:{dt.minute : 03}"

def seaborn_boxplot_combined(
    df: 'DataFrame',
    outfile: str,
):
    import seaborn as sns
    from matplotlib.ticker import FuncFormatter

    def f():
        # even if seaborn allowed datetimes, numpy couldn't add them for some reason
        df.Arrive = df.Arrive.view(int) / 1e12
        sns.boxplot(
            data=df, x='Arrive', y='Station', hue='Line',
            flierprops={'markersize': 1, 'linestyle': 'none'}
        )

    def g():
        plt.grid(which='both', alpha=0.7)
        plt.gca().tick_params(axis='x', which='minor')
        plt.gca().yaxis.set_tick_params(labelright='on')
        plt.gca().xaxis.set_major_formatter(FuncFormatter(format_int_time))
        plt.gca().xaxis.set_tick_params(labeltop='on')
        plt.tight_layout()

    return core(outfile, f, g, 'boxplot_combined', (15, 20))

# only plots main branch
def seaborn_boxplot(
    df: 'DataFrame',
    line_name: str, plot_name: str,
    color: str,
):
    import seaborn as sns
    from matplotlib.ticker import FuncFormatter

    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.png'

    def f():
        # even if seaborn allowed datetimes, numpy couldn't add them for some reason
        df.Arrive = df.Arrive.view(int) / 1e12
        sns.boxplot(data=df, x='Arrive', y='Station', color=color)
        # Gets too thin at the end (because too few stations), so boxplots are better
        # This is why a ridgeline (https://seaborn.pydata.org/examples/kde_ridgeplot.html)
        # plot won't work -- height of distribution too small
        #sns.violinplot(data=df, x='Arrive', y='Station', color=color)
        # This one needs change the division from 1e12 to 1e6
        #sns.kdeplot(data=df, x="Arrive", hue='Station')

    def g():
        plt.grid(which='both', alpha=0.7)
        plt.gca().tick_params(axis='x', which='minor')
        plt.gca().xaxis.set_major_formatter(FuncFormatter(format_int_time))
        plt.gca().xaxis.set_tick_params(labeltop='on')
        plt.gca().yaxis.set_tick_params(labelright='on')
        plt.tight_layout()

    return core(outfile, f, g, 'boxplot', (15, 15))

def matplotlib(
    df: 'DataFrame', df_for_branch: 'Optional[DataFrame]',
    line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    outfile = Constants.plot_dir / f'{line_name}_{plot_name}.png'

    def f():
        args = dict(
            color=color,
            alpha=alpha,
            marker='o'
        )
        if not line:
            args.update(dict(linestyle='None'))  # Must be a string!

        # yikes
        col = 'Station' if df_for_branch is None else 'Station_sequence'

        for train in df.Train.unique():
            plt.plot(
                df[df.Train == train]['Arrive'],
                df[df.Train == train][col],
                **args
            )

        if df_for_branch is not None:
            branch_color = 'tab:blue'
            args['color'] = branch_color
            for train in df_for_branch.Train.unique():
                plt.plot(
                    df_for_branch[df_for_branch.Train == train]['Arrive'],
                    df_for_branch[df_for_branch.Train == train][col],
                    **args
                )

    def g():
        format_mpl_plot(plt.gca())
        plt.tight_layout()

    return core(outfile, f, g, plot_name, (15, 15))

def plot_ax_core(
    df: 'DataFrame',
    alpha: float,
    color: str, line: bool,
    ax: 'Optional[Axis]' = None
):

    plt.rcParams['font.family'] = 'Hiragino Sans GB'
    if ax is None:
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
            df[df.Train == train]['Station'],
            **args
        )
    return ax

def format_mpl_plot(ax):
    # This has to be separated for some reason
    from matplotlib.dates import DateFormatter
    from matplotlib.ticker import AutoMinorLocator
    ax.grid(which='both', alpha=0.7)
    ax.tick_params(axis='x', which='minor')
    ax.invert_yaxis()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    ax.xaxis.set_tick_params(labeltop='on')
    ax.yaxis.set_tick_params(labelright='on')

def bokeh(
    df: 'DataFrame', df_for_branch: 'Optional[DataFrame]',
    line_name: str, plot_name: str, alpha: float,
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
    df: 'DataFrame', df_for_branch: 'Optional[DataFrame]',
    line_name: str, plot_name: str, alpha: float,
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

