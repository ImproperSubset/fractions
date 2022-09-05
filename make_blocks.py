#!/usr/bin/env python3

import os
import fire
from fraction_blocks import FractionBlocks

denominators: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16]


def make_blocks(prefix: str = 'fb') -> None:

    for denominator in denominators:
        match denominator:
            case 9|10|12|16:
                block: FractionBlocks = FractionBlocks(denominator=denominator,
                 label_font_size = 9, label_divider_scale = 0.7, label_position=2)
            case _:
                block: FractionBlocks = FractionBlocks(denominator=denominator)

        filename_prefix: str = f'{prefix}_{block.numerator}_{block.denominator}'
        block.filename=f'{filename_prefix}.scad'

        block.pie_slice()
        os.system(f'openscad -o {filename_prefix}.stl --export-format binstl {filename_prefix}.scad --quiet')

    FractionBlocks(filename=f'{prefix}_pie_pan.scad').pie_pan()
    os.system(f'openscad -o {prefix}_pie_pan.stl --export-format binstl {prefix}_pie_pan.scad --quiet')



if __name__ == "__main__":
    fire.Fire(make_blocks)
