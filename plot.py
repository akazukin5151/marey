from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import AutoMinorLocator
from common import mkdirs_touch_open


def main(
    df: 'pd.DataFrame', line_name: str, plot_name: str, alpha: float,
    color: str, line: bool,
):
    outfile = Path(f'plots/{line_name}_{plot_name}.png')
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

