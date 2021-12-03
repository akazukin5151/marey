import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import plot
from common import Constants
from prepare_plot import subtract_min, groupby_apply_midnight


def read_delta_csv(line_name):
    return pd.read_csv(
        Constants.gen_csv_dir / f'{line_name}_delta.csv',
        parse_dates=['Arrive', 'Depart']
    )

def delta(line1, line2, fixes):
    return delta_inner('', True, line1, line2, fixes)

def delta_scatter(line1, line2, fixes):
    return delta_inner('_scatter', False, line1, line2, fixes)

def delta_inner(
    modifier: str,
    draw_line: bool,
    line1: 'Line',
    line2: 'Line',
    fixes: 'Optional[List[(str, str)]]' = None
):
    '''Given two lines, plot them together in the same axis,
    optionally fixing their station names.

    Run with fixes=None first, inspect the output and plot, then pass in a fix

    If fixes is None, then it will use an algorithm to find stations that only
    one line has, print it, and generate a plot.

    Stations that only one line has will make the plot look wrong, so if
    such stations exist, it is encouraged to fix them by passing in fixes

    fixes is a list of 2-tuples. The items of the tuples are both strings
    representing two different station names on the two lines.
    The tuple represent that the y-label of the two stations should be fused
    eg ('a', 'b') means stations called 'a' and 'b' will be both renamed to 'a/b'

    There should be a tuple for every station that only one line has
    '''
    outfile = Constants.plot_dir / (
        line1.name + '_' + line2.name + f'_combined_delta{modifier}.png'
    )
    if outfile.exists():
        return

    print('Plotting combined (offline)...')
    df1 = read_delta_csv(line1.name + '_main')
    df2 = read_delta_csv(line2.name + '_main')

    if fixes is None:
        # get all unique stations sequences
        df1_stations = df1.groupby('Train').Station.unique().apply(tuple)
        df2_stations = df2.groupby('Train').Station.unique().apply(tuple)
        # find train with most stations
        df1_longest_train = df1_stations.apply(len).idxmax()
        df2_longest_train = df2_stations.apply(len).idxmax()
        # Select only the stations on that train
        df1_stations_longest = df1[df1.Train == df1_longest_train].Station
        df2_stations_longest = df2[df2.Train == df2_longest_train].Station
        print(find_need_to_fix(df1_stations_longest, df2_stations_longest))
    else:
        for (a, b) in fixes:
            fused = a + '/' + b
            # where doesn't work for some reason
            df1.replace(a, fused, inplace=True)
            df2.replace(b, fused, inplace=True)
            df1.replace(b, fused, inplace=True)
            df2.replace(a, fused, inplace=True)

    # Plot order doesn't matter
    ax = plot.plot_ax_core(
        df1, alpha=0.2, color=line1.color, line=draw_line,
    )
    ax = plot.plot_ax_core(
        df2, alpha=0.2, color=line2.color, line=draw_line, ax=ax,
    )
    custom_lines = [
        Line2D([0], [0], color=line1.color, marker='o'),
        Line2D([0], [0], color=line2.color, marker='o')
    ]

    plot.format_mpl_plot(ax)
    plt.legend(custom_lines, [line1.name, line2.name])
    plt.tight_layout()
    plt.savefig(outfile)

def delta_box(
    line1: 'Line',
    line2: 'Line',
    fixes: 'Optional[List[(str, str)]]' = None
):
    outfile = Constants.plot_dir / (
        line1.name + '_' + line2.name + '_combined_delta_box.png'
    )
    if outfile.exists():
        return

    print('Plotting combined (offline)...')
    df1 = read_delta_csv(line1.name + '_main')
    df2 = read_delta_csv(line2.name + '_main')

    if fixes is None:
        # get all unique stations sequences
        df1_stations = df1.groupby('Train').Station.unique().apply(tuple)
        df2_stations = df2.groupby('Train').Station.unique().apply(tuple)
        # find train with most stations
        df1_longest_train = df1_stations.apply(len).idxmax()
        df2_longest_train = df2_stations.apply(len).idxmax()
        # Select only the stations on that train
        df1_stations_longest = df1[df1.Train == df1_longest_train].Station
        df2_stations_longest = df2[df2.Train == df2_longest_train].Station
        print(find_need_to_fix(df1_stations_longest, df2_stations_longest))
    else:
        for (a, b) in fixes:
            fused = a + '/' + b
            # where doesn't work for some reason
            df1.replace(a, fused, inplace=True)
            df2.replace(b, fused, inplace=True)
            df1.replace(b, fused, inplace=True)
            df2.replace(a, fused, inplace=True)

    df1['Line'] = line1.name
    df2['Line'] = line2.name
    df = pd.concat([df1, df2])
    plot.seaborn_boxplot_combined(df, outfile)

def find_need_to_fix(s1: 'Series[a]', s2: 'Series[a]') -> '[(int, a)]':
    '''Try to match stations from the two Series, returning potential
    stations that need to be corrected manually

    Once a mismatch is found, it can mean a few things:
    1) One of the Series is skipping that station
      a) [a, b, c, d] and [a, c, d]  (singular)
      b) [a, b, c, d] and [a, d]  (multiple)
    2) One of the Series goes to (an) alternative(s) station
      a) [a, b, c, d] and [a, e, c, d]  (equal, singular)
      b) [a, b, c, d] and [a, e, f, d]  (equal, multiple)
      c) [a, b, c, d] and [a, e, f, g, d]  (non-equal, multiple)
    3) The Series are permanently branching
      a) [a, b, c, d] and [a, b, e, f]  (branching at the end)
      b) [a, b, c, d] and [e, f, c, d]  (branching at the start)

    case 1 doesn't matter because the plot will correctly handle that
    ignore case 3a for now, the stations after the branch are likely
    going to be outside the "area of interest" anyway
    case 2 needs to be fixed, but that's not possible automatically with an algorithm,
    but it is at least possible to identify where it happens
    '''
    # (slower = more stations)
    slower_line, longer_line = (s1, s2) if len(s1) > len(s2) else (s2, s1)
    slower_line = slower_line.drop_duplicates()
    longer_line = longer_line.drop_duplicates()

    case_twos = []
    slow_i = long_i = 0
    while slow_i < len(slower_line) and long_i < len(longer_line):
        slow_item = slower_line.iloc[slow_i]
        long_item = longer_line.iloc[long_i]
        if slow_item == long_item:
            slow_i += 1
            long_i += 1
        elif long_item in slower_line.values:
            # We found case 1
            # Keep increasing slow_i and match. Eventually we'll hit a point
            # where this long_item equals a slow_item
            slow_i += 1
        else:
            # long_item is a case 2
            case_twos.append((long_i, long_item))
            # This only works for (equal, singular)
            # If the next station in the long line is in the short line
            # then continue matching the next station in the long line
            # with stations in the short line
            if longer_line.iloc[long_i + 1] in slower_line.values:
                long_i += 1
            # else:
            # This is when the two lines branch (case 3), ignore it
    return case_twos


def remove_stations(f, station: str, df):
    for train in df.Train.unique():
        this_train = df[df.Train == train]
        idx_eq = this_train[this_train['Station'] == station].index
        if len(idx_eq) == 0:
            continue
        idxes = f(idx_eq[0], this_train.index)
        df.drop(index=idxes, inplace=True)

def remove_stations_after(station: str, df):
    return remove_stations(lambda x, y: range(x, y[-1] + 1), station, df)

def remove_stations_before(station: str, df):
    return remove_stations(lambda x, y: range(y[0], x), station, df)

def shift_times(dfs, base_idx: int, target_idx: int, base_station: str):
    incr = (
        dfs[base_idx][dfs[base_idx].Station == base_station].Arrive.mean()
    ) - Constants.midnight
    dfs[target_idx].Arrive = dfs[target_idx].Arrive + incr

def delta_subsets(d: '(Line, Optional[str], Optional[str])]', shifts, fixes):
    lines = [x for x, _, _ in d]
    starts = [start for _, start, _ in d]
    ends = [end for _, _, end in d]
    return delta_subsets_inner('', True, lines, starts, ends, shifts, fixes)

def delta_subsets_scatter(
    d: '(Line, Optional[str], Optional[str])]',
    shifts, fixes
):
    lines = [x for x, _, _ in d]
    starts = [start for _, start, _ in d]
    ends = [end for _, _, end in d]
    return delta_subsets_inner('_scatter', False, lines, starts, ends, shifts, fixes)

def delta_subsets_inner(
    modifier: str,
    draw_line: bool,
    lines: 'List[Line]',
    starts: 'List[str]',
    ends: 'List[str]',
    shifts: 'List[(int, int, str)]',
    fixes: 'Optional[List[(str, str)]]' = None
):
    '''Given a list of Lines, plot all lines together in the same axis,
    limiting the stations to start at `starts` and end at `ends` for each line

    len(lines) == len(starts) == len(ends) should be satisfied, but if not,
    excess items at the end is ignored
    '''
    line_names = [line.name for line in lines]
    outfile = Constants.plot_dir / (
        '_'.join(line_names) + f'_combined_delta{modifier}.png'
    )
    if outfile.exists():
        return

    print('Plotting combined (offline)...')
    dfs = [read_delta_csv(line.name + '_main') for line in lines]

    for idx, (df, station) in enumerate(zip(dfs, starts)):
        # This is looping twice if condition is true...
        if station is not None:
            remove_stations_before(station, df)
        dfs[idx] = groupby_apply_midnight(df, subtract_min)

    for shift in shifts:
        shift_times(dfs, shift[0], shift[1], shift[2])

    for df, station in zip(dfs, ends):
        if station is not None:
            remove_stations_after(station, df)

    if fixes:
        for (a, b) in fixes:
            fused = a + '/' + b
            for df in dfs:
                df.replace(a, fused, inplace=True)
                df.replace(b, fused, inplace=True)

    # Plot order doesn't matter
    ax = None
    for df, line in zip(dfs, lines):
        ax = plot.plot_ax_core(
            df, alpha=0.2, color=line.color, line=draw_line, ax=ax
        )

    custom_lines = [
        Line2D([0], [0], color=line.color, marker='o')
        for line in lines
    ]

    plot.format_mpl_plot(ax)
    plt.legend(custom_lines, line_names)
    plt.tight_layout()
    plt.savefig(outfile)
