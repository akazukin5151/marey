from .common import Constants
from marey.lib import prepare_plot

def prepare_normal(line_name):
    return prepare_plot.prepare_normal(
        in_csv=Constants.gen_csv_dir / f'{line_name}.csv',
        out_csv=Constants.gen_csv_dir / f'{line_name}_processed.csv'
    )
