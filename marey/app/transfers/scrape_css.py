from typing import List
from pathlib import Path
from .common import CssClass

HEX_LEN = 6

def main(stylesheet_path: Path, color_classes: List[CssClass]) -> List[str]:
    with open(stylesheet_path, 'r') as f:
        css = f.read()

    colors = []
    for color_class in color_classes:
        if color_class == 'walk':
            continue

        class_pos = css.find(f'.{color_class}.with-bg')
        color_key = css.find('background-color', class_pos)

        start = color_key + len('background-color: ')
        colors.append(css[start : start + HEX_LEN + 1])

    return colors
