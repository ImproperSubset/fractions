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

    Blocks are rendered to STL files for printing. 
    """

    filename: str = "output.stl"
    """name of the desired output file"""

    # if we're printing a pie slice, then this is the numerator
    # and denomenator of the fraction we're representing
    numerator: int = 1
    denominator: int = 3

    # This specifies the dimensions of a pie slice in mm. These
    # dimensions are also used to compute the dimensions a pie
    # pan that can hold the slices.
    pie_radius: int = 50
    pie_height: int = 10

    # The inner diameter of the pie pan is twice the radius of a pie
    # slice plus this gap in millimeters.
    pie_pan_gap: int = 3

    # Specifies how thickness of the bottom and wall of the pie pan
    pan_thickness: int = 3
    pan_wall: int = 3

    # Additional distance to move label away from center of the pie in mm
    text_position: int = 3

    # You know the line between the numerator and the denominator?
    # Apparently, it's called the vinculum? For small fractions, the
    # vinculum can fall off the edge of a pie slice. This is a scaling
    # factor that controls the width of the vinulum. Set it to .9 to get
    # a vinculum 90% as wide as the default.
    divider_bar: float = 1

    # Approximate height of text in mm. The layout would like this to be
    # around 25% of the radius.
    text_size: int = 13

    # If use_default_tweaks is set to True, the code will make some adjustments to get
    # the text to fit given the defaults above. Set to False if you want to make your
    # own tweaks above.
    #use_default_tweaks = True

    # Some edges of have a fillet to make them less
    # painful to step on. This is the radius of the fillet.
    fillet: int = 1

    # Wherever we use openscad to render a curve, this parameter
    # controls the smoothness of the curve.
    segments: int = 90

    _angle: float = dataclasses.field(init=False)
    _scad_file: str = dataclasses.field(init=False)
    _stl_file: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._angle = 360 * self.numerator / self.denominator

    def _assemble_text(self, string: str) -> text:
        return text(
            text=string, valign='center', halign='center', size=self.text_size
        )

    def _assemble_label(self):

        divide = self.pie_radius / 2
        return union()(
            rotate(a=-90)(
                linear_extrude(height=0.2 * self.pie_height)(
                    translate(v=(0, divide / 2 + self.text_position,0))(
                        rotate(a=180)(self._assemble_text(str(self.numerator)))
                    ),
                    translate(v=(0, divide - .05 * self.pie_radius + self.text_position,0))(
                        scale(v=(self.divider_bar, 1, 1))(self._assemble_text('\u2015'))
                    ),
                    translate(v=(0, divide + divide / 2 + self.text_position,0))(
                        rotate(a=180)(self._assemble_text(str(self.denominator)))
                    )
                )
            )
        ) # yapf: disable


    def _assemble_slice(self):
        return rotate_extrude(self._angle, segments=self.segments)(
            translate((self.fillet, self.fillet, 0))(offset(r=self.fillet)(
                square((self.pie_radius - 2 * self.fillet, self.pie_height - 2 * self.fillet)))
            )
        ) # yapf: disable


    def _assemble_pie_slice(self):

        return union()(
            translate(v=(0, 0, self.pie_height))(
                rotate(a=self._angle / 2)(self._assemble_label())
            ),
            self._assemble_slice()
        ) # yapf: disable


    def _assemble_pie_pan(self):
        inner = self.pie_radius + self.pie_pan_gap
        outer = inner + self.pan_wall
        return difference()(
            cylinder(r=outer, h=self.pan_thickness + self.pie_height*0.8, segments=self.segments),
            translate(v=(0, 0,self.pan_thickness))(
                cylinder(r=inner,h=self.pie_height,segments=self.segments)
            )
        ) # yapf: disable


    def pie_slice(self) -> None:
        scad_render_to_file(
            self._assemble_pie_slice(), self.filename, include_orig_code=True
        )

    def pie_pan(self) -> None:
        scad_render_to_file(
            self._assemble_pie_pan(), self.filename, include_orig_code=True
        )

    def test(self) -> None:
        test_assembly = self._assemble_pie_pan()
        test_assembly += translate(v=(0, 0, self.pan_thickness))(
            self._assemble_pie_slice()
        ) # yapf:disable
        scad_render_to_file(
            test_assembly, self.filename, include_orig_code=True
        )


if __name__ == '__main__':
    fire.Fire(FractionBlocks)
