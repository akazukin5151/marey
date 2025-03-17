from pathlib import Path
import matplotlib.pyplot as plt
from marey.lib import plot
import pandas as pd

def main(
    dfs: list[tuple[str, str, list[pd.DataFrame]]],
    plot_outfile: Path,
):
    def f():
        labelled = {}
        for (line_name, color, dfs_) in dfs:
            for df in dfs_:
                if labelled.get(line_name, None) is None:
                    label = line_name
                else:
                    label = None

                plt.plot(
                    df["Arrive"],
                    df["Station"],
                    marker="o",
                    color=color,
                    label=label,
                )

                labelled[line_name] = True

        plt.legend()

    def g():
        plot.format_mpl_plot(plt.gca())
        plt.tight_layout()

    return plot.core(plot_outfile, f, g, 'transfer', (15, 15))
