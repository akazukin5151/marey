from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import AutoMinorLocator
from common import mkdirs_touch_open


def main(line_name, df):
    plt.rcParams['font.family'] = 'Hiragino Sans GB'

    plt.figure(figsize=(15, 15))
    # yikes
    for train in df.Train.unique():
        plt.plot(
            df[df.Train == train]['Arrive'],
            df[df.Train == train]['Station'],
            marker='o',
            color='orange'
        )
    plt.grid(which='both', alpha=0.7)
    plt.gca().tick_params(axis='x', which='minor')
    plt.gca().invert_yaxis()
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
    plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plt.gca().xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    plt.gca().xaxis.set_tick_params(labeltop='on')
    plt.tight_layout()
    outfile = Path(f'plots/{line_name}.png')
    mkdirs_touch_open('', outfile)
    plt.savefig(outfile)

    # TODO plot duration from first station

