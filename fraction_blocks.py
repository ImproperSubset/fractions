#!/usr/bin/env python3
# *_* coding: utf-8 *_*
"""
python script for generating 3D printable fraction blocks
"""

import dataclasses
from dataclasses import dataclass

from solid import scad_render_to_file
from solid.objects import (
    union, offset, difference, square, rotate_extrude, text, translate, rotate,
    linear_extrude, scale, cylinder
)

import fire


@dataclass(kw_only=True)
class FractionBlocks:
    """
    python script for generating 3D printable fraction blocks

    This script uses SolidPython and OpenSCAD to create 3D printable
    blocks that model fractions. The blocks represent fractions as
    sectors of a circle where the angle of the sector is 2π radians
    multiplied by the fraction. So, the model of the fraction ¼ is a
    sector whose angle is 90 degrees.

    The script uses a pie analogy to refer to the blocks it produces.
    The script refers to sector shaped blocks as pie slices. The script
    can produce a pie pan which is a dish shaped container that conforms
    to the dimensions of the pie slices and allows multiple pie slices
    to be arranged together.

    The script provides controls that control the dimensions of the pie
    slices and pie pan. For testing purposes, the script can also produce
    an unprintable test output that composes a pie slice with a pie pan
    to provide a visualization of the output.

    Blocks are rendered to .scad files and require processing by OpenSCAD
    to generate STL files.

    Args:
        filename (str): name of the desired output file
        numerator (int): the numerator of the fraction (default = 1)
        denominator (int): the denominator of the fraction (default = 3 mm)
        slice_radius (int): the radius of a pie slice (default = 50 mm)
        slice_height (int): the height of a pie slice (default = 10 mm)
        slice_pan_gap (int): extra space to loosen slices in the pan (default = 2 mm)
        pan_floor_height (int): the thickness of the pie pan's floor (default = 3 mm)
        pan_wall_width (int): the width of the pan's wall (default = 3 mm)
        label_position (int): adjusts position of label on slice (default = 3 mm)
        label_divider_scale (float): scales the width of the vinculum (default = 1.0)
        label_font_size (int): approximate height of label font (default = 13 mm)
        fillet (int): radius of fillets (default = 2 mm)
        segments (int): larger values make circles more circular (default = 200)

    """

    # Desired name of the output file
    filename: str = "output.stl"

    # If we're printing a pie slice, then this is the numerator
    # and denomenator of the fraction we're modeling.
    numerator: int = 1
    denominator: int = 3

    # This specifies the dimensions of a pie slice in mm. These
    # dimensions are also used to compute the dimensions a pie
    # pan that can hold the slices.
    slice_radius: int = 50
    slice_height: int = 10

    # The distance from the center of the pie pan to the inner
    # side of the pan's wall is the radius of a pie slice plus
    # this value. It leaves some extra space for the pie slice
    # blocks to be easily inserted and removed from the pan.
    # This game is measured in mm.
    slice_pan_gap: int = 2

    # Specifies how thickness of the bottom and wall of the pie pan
    pan_floor_height: int = 3
    pan_wall_width: int = 3

    # Additional distance to move label away from center of the pie in mm
    label_position: int = 3

    # You know the line between the numerator and the denominator?
    # Apparently, it's called the vinculum? For small fractions, the
    # vinculum can fall off the edge of a pie slice. This is a scaling
    # factor that controls the width of the vinulum. Set it to .9 to get
    # a vinculum 90% as wide as the default.
    label_divider_scale: float = 1

    # Approximate height of text in mm. The layout would like this to be
    # around 25% of the radius.
    label_font_size: int = 13

    # Some edges of have a fillet to make them less
    # painful to step on. This is the radius of the fillet.
    fillet: int = 2

    # Wherever we use openscad to render a curve, this parameter
    # controls the smoothness of the curve.
    segments: int = 200

    _angle: float = dataclasses.field(init=False)
    _scad_file: str = dataclasses.field(init=False)
    _stl_file: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._angle = 360 * self.numerator / self.denominator

    def _assemble_text(self, string: str) -> text:
        return text(
            text=string,
            valign='center',
            halign='center',
            size=self.label_font_size
        )

    def _assemble_label(self):

        divide = self.slice_radius / 2
        return union()(
            rotate(a=-90)(
                linear_extrude(height=0.2 * self.slice_height)(
                    translate(v=(0, divide / 2 + self.label_position,0))(
                        rotate(a=180)(self._assemble_text(str(self.numerator)))
                    ),
                    translate(v=(0, divide - .05 * self.slice_radius + self.label_position,0))(
                        scale(v=(self.label_divider_scale, 1, 1))(self._assemble_text('\u2015'))
                    ),
                    translate(v=(0, divide + divide / 2 + self.label_position,0))(
                        rotate(a=180)(self._assemble_text(str(self.denominator)))
                    )
                )
            )
        ) # yapf: disable


    def _assemble_slice(self):
        return rotate_extrude(self._angle, segments=self.segments)(
            translate((self.fillet, self.fillet, 0))(offset(r=self.fillet)(
                square((self.slice_radius - 2 * self.fillet, self.slice_height - 2 * self.fillet)))
            )
        ) # yapf: disable


    def _assemble_pie_slice(self):

        return union()(
            translate(v=(0, 0, self.slice_height))(
                rotate(a=self._angle / 2)(self._assemble_label())
            ),
            self._assemble_slice()
        ) # yapf: disable


    def _assemble_pie_pan(self):
        inner = self.slice_radius + self.slice_pan_gap
        outer = inner + self.pan_wall_width
        return difference()(
            cylinder(r=outer,
                h=self.pan_floor_height + self.slice_height*0.8,
                segments=self.segments),
            translate(v=(0, 0,self.pan_floor_height))(
                cylinder(r=inner,h=self.slice_height,segments=self.segments)
            )
        ) # yapf: disable


    def pie_slice(self) -> None:
        """Generate OpenSCAD code for the specified pie slice"""
        scad_render_to_file(
            self._assemble_pie_slice(), self.filename, include_orig_code=True
        )

    def pie_pan(self) -> None:
        """Generate OpenSCAD code for a pie pan that fits the specified pie slice"""
        scad_render_to_file(
            self._assemble_pie_pan(), self.filename, include_orig_code=True
        )

    def test(self) -> None:
        """Generate OpenSCAD code for a test fit of the specified pie slice
        in a pie pan. This is provided to visualize the specified components.
        It should not be printed. It should only be rendered for testing.
        """
        test_assembly = self._assemble_pie_pan()
        test_assembly += translate(v=(0, 0, self.pan_floor_height))(
            self._assemble_pie_slice()
        ) # yapf:disable
        scad_render_to_file(
            test_assembly, self.filename, include_orig_code=True
        )


if __name__ == '__main__':
    fire.Fire(FractionBlocks)
