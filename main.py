#! /usr/bin/env python3
import viewscad

from solid import scad_render_to_file
from solid.objects import (union, cube, offset, difference, square, rotate_extrude, text, translate, rotate, linear_extrude, scale,
                           cylinder, hole, circle)

# The fraction
numerator = 1     # numerator of the fraction
denominator = 3   # denominator of the fraction

segments = 90
slop = .03
fillet = 1

# The size of the pie slices
radius = 50       # radius of the complete pie slice in mm
height = 10        # height of the pie slice in mm

# The Base
make_base = False  # if true, render the base or maybe it's the 1/1 fraction
test_fit = False   # if make_base and this are both true, render an unprintable STL
                   # used to for testing to see how proportions look
thickness = .25 * height       # This vertical thickness of the base piece
edge_thickness = .25 * height  # The thickness of the base piece's wall

# Parameters for the size of the text
text_position = .05 * radius  # tweak factor to move text away from center of the pie
divider_bar = 1               # scaling constant for the width of the divider bar
text_size = radius/4          # approximate height of text in mm

# If use_default_tweaks is set to True, the code will make some adjustments to get
# the text to fit given the defaults above. Set to False if you want to make your
# own tweaks above.
use_default_tweaks = True

if use_default_tweaks:
    match (numerator, denominator):
        case (1, 16):
            text_size = radius/6
            divider_bar = .5    # tweak factor to reduce the width of the divider bar
        case (1, 12):
            divider_bar = .75   # tweak factor to reduce the width of the divider bar
        case (1, 10):
            divider_bar = .9    # tweak factor to reduce the width of the divider bar

# Convenience constants. Below here the code isn't expecting any parameterization changes.
angle = 360*(numerator/denominator)  # degrees
n = numerator
d = denominator


def ftext(s: str) -> object:
    return text(text=s, valign='center',
                halign='center', size=text_size)


def label() -> object:

    divide = radius/2
    rv = union()(
        rotate(a=-90)(
            linear_extrude(height=0.2*height)(
                translate(v=(0, divide/2+text_position))(
                    rotate(a=180)(
                        ftext(str(n))
                    )),
                translate(v=(0, divide-.05*radius+text_position))(
                    scale(v=(divider_bar, 1, 1))(ftext('\u2015'))
                ),
                translate(v=(0, divide+divide/2+text_position))(
                    rotate(a=180)(
                        ftext(str(d))
                    ))
            )))

    return rv


def slice() -> object:
    rv = rotate_extrude(angle=360*n/d, segments=segments)(
        translate((fillet, fillet, 0))(offset(r=fillet)(
            square((radius-2*fillet, height-2*fillet))))
    )
    return rv


def fraction():
    rv = union()(
        translate(v=(0, 0, height))(rotate(a=angle/2)(label())),
        slice()
    )

    return rv


def base():
    inner = radius+slop*radius
    outer = inner + edge_thickness
    rv = difference()(
        cylinder(r=outer, h=height*.8, segments=segments),
        translate(v=(0, 0, thickness))(
            cylinder(r=inner, h=height*.8, segments=segments)
        )
    )
    return rv


if __name__ == '__main__':
    if make_base:
        a = base()
        if test_fit:
            a += translate(v=(0,0,thickness))(fraction())
    else:
        a = fraction()
    

    scad_render_to_file(a, include_orig_code=True)
