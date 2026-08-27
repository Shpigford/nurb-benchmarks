from nurb import *


@part
def bundle_holder(bundle_diameter: float = 8.0):
    """Wall-mounted open channel for a horizontal cable bundle.

    bundle_diameter: measured width across the cable bundle
    """
    clearance = 0.4
    channel_width = bundle_diameter + clearance

    length = 12.0
    back_thickness = 2.4
    back_height = channel_width + 11.6
    floor_thickness = 1.2
    outer_wall_thickness = 1.2
    outer_wall_height = floor_thickness + channel_width * 0.68

    screw_hole_diameter = 4.4
    screw_height = channel_width + 7.0

    back = Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        channel_width + outer_wall_thickness,
        length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((back_thickness, 0, 0))
    outer_wall = Box(
        outer_wall_thickness,
        length,
        outer_wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((back_thickness + channel_width, 0, 0))

    screw_bore = Cylinder(
        screw_hole_diameter / 2,
        back_thickness + 0.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90).translate((-0.2, length / 2, screw_height))

    return back + floor + outer_wall - screw_bore
