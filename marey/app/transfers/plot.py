from typing import List
from pathlib import Path
import matplotlib.pyplot as plt
from marey.lib import plot

def main(dfs, plot_outfile: Path, colors: List[str]):
    def f():
        for (df, color) in zip(dfs, colors):
            plt.plot(df['Arrive'], df['Station'], marker='o', color=color)

    def g():
        plot.format_mpl_plot(plt.gca())
        plt.tight_layout()

    return plot.core(plot_outfile, f, g, 'transfer', (15, 15))
