"""A compact wall-mounted holder for a horizontal cable bundle."""

from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter")):
    """Wall-mounted cable holder.

    bundle_diameter: diameter of the cable bundle that runs along Y
    """

    # The screw occupies the low/back corner.  The cable is deliberately
    # stood off beyond the screw head so the two can coexist without a
    # special-purpose relief cut through the retaining rails.
    length = 16.0
    back_thickness = 2.8
    back_height = max(10.0, bundle_diameter + 2.0 * 0.4 + 2.0)

    floor_thickness = 2.0
    rail_thickness = 2.0
    bundle_clearance = 0.4
    screw_head_depth = 3.2
    bundle_left = back_thickness + screw_head_depth + 0.8
    bundle_center_x = bundle_left + bundle_diameter / 2.0
    front_inner_x = bundle_left + bundle_diameter + bundle_clearance
    front_outer_x = front_inner_x + rail_thickness

    bundle_center_z = floor_thickness + bundle_diameter / 2.0 + bundle_clearance
    front_height = floor_thickness + bundle_diameter + 2.0 * bundle_clearance

    # Put the retaining section beyond the 8.4 mm head-and-driver sweep.
    screw_hole_radius = 4.4 / 2.0
    # Keep the through-bore well inside the plate so the screw seat has a
    # printable ring of material on every side.
    screw_y = screw_hole_radius + 1.2
    screw_z = screw_hole_radius + 1.2
    head_sweep_radius = 8.4 / 2.0
    retaining_start_y = screw_y + head_sweep_radius + 0.3
    retaining_length = length - retaining_start_y

    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be positive", param="bundle_diameter")
    if retaining_length < length / 3.0:
        reject("bundle_diameter is too large for the retaining section; reduce it", param="bundle_diameter")

    back = Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    floor = Pos(back_thickness - 0.05, retaining_start_y, 0) * Box(
        front_outer_x - back_thickness + 0.05,
        retaining_length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    front_rail = Pos(front_inner_x, retaining_start_y, 0) * Box(
        rail_thickness,
        retaining_length,
        front_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = back + floor + front_rail

    # A straight 4.4 mm bore opens on the X-min back face and stops at the
    # far side of the 2.8 mm mounting plate, where the head seats.
    bore = (
        Pos(-0.1, screw_y, screw_z)
        * Rot(0, 90, 0)
        * Cylinder(
            screw_hole_radius,
            back_thickness + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )

    return body - bore
