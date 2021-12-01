import pandas as pd
import matplotlib.pyplot as plt
import plot
from common import Constants


def read_delta_csv(line_name):
    return pd.read_csv(
        Constants.gen_csv_dir / f'{line_name}_delta.csv',
        parse_dates=['Arrive', 'Depart']
    )

def delta(line1: 'Line', line2: 'Line', fixes: 'Optional[List[(str, str)]]' = None):
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
    # TODO multiple lines
    outfile = Constants.plot_dir / (line1.name + '_' + line2.name + '_combined.png')
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
        df1,
        alpha=0.2, color=line1.color, line=True
    )
    ax = plot.plot_ax_core(
        df2,
        alpha=0.2, color=line2.color, line=True, ax=ax
    )
    plot.format_mpl_plot(ax)
    plt.tight_layout()
    plt.savefig(outfile)

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
            if longer_line.iloc[long_i+1] in slower_line.values:
                long_i += 1
            # else:
            # This is when the two lines branch (case 3), ignore it
    return case_twos

