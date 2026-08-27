from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip for a cable bundle.

    bundle_diameter: measured bundle size; the holder adds 0.4 mm fit clearance
    and scales the cradle width and height from it.
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be positive", param="bundle_diameter")

    # Coordinates are the mounting coordinates: X is out from the wall, Y is
    # along the cable, and Z is up.  The back plate and the cradle both start
    # on the bed, so the whole holder prints in its mounting orientation.
    length = 26.0
    back_thickness = 2.6
    back_height = bundle_diameter + 6.0
    bundle_clearance = 0.4
    cavity_width = bundle_diameter + bundle_clearance
    bottom_thickness = 3.0
    rail_thickness = 2.2
    rail_height = bundle_diameter + 4.0

    retention_length = 9.0
    retention_y = -retention_length / 2.0
    y_min = -length / 2.0

    back = Pos(0, y_min, 0) * Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    cradle = Pos(back_thickness, retention_y, 0) * Box(
        cavity_width,
        retention_length,
        bottom_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    rail = Pos(back_thickness + cavity_width, retention_y, 0) * Box(
        rail_thickness,
        retention_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    holder = back + cradle + rail

    # M4 medium clearance bore, normal to the wall.  It is deliberately at
    # the end of the plate: the screw head and driver clear the cradle span.
    screw_hole_diameter = 4.4
    screw_y = -9.0
    screw_z = back_height / 2.0
    bore = Pos(-0.2, screw_y, screw_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole_diameter / 2.0,
        back_thickness + 0.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    holder = holder - bore

    # Fit-critical cradle edges stay sharp.  The optional draft flag is kept
    # for the viewer's fast rebuild path; the functional solid is already
    # support-free without cosmetic dress-up.
    return holder
