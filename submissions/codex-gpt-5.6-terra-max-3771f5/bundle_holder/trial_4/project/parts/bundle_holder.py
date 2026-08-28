from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A one-screw wall holder for a horizontal cable bundle.

    bundle_diameter: measured diameter of the cable bundle the channel holds.
    """
    # The 0.4 mm fit allowance is deliberately kept on each constrained side of
    # the bundle. The wall provides the fourth, rearward restraint after mounting.
    fit_clearance = 0.4
    back_thickness = 3.8
    shelf_thickness = 2.0
    rail_thickness = 2.0
    holder_length = 14.0

    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    channel_width = bundle_diameter + 2.0 * fit_clearance
    rail_inner_x = back_thickness + channel_width
    bundle_center_z = shelf_thickness + fit_clearance + bundle_diameter / 2.0
    rail_height = bundle_center_z + bundle_diameter / 2.0

    # Keep the M4 head-and-driver clearance entirely above the cable envelope.
    screw_hole_diameter = 4.4
    screw_head_clearance_diameter = 9.0
    screw_seat_x = 2.6
    screw_y = holder_length / 2.0
    screw_z = rail_height + screw_head_clearance_diameter / 2.0 + 1.0
    back_height = screw_z + screw_head_clearance_diameter / 2.0 + 1.0

    # All three members share material: the back mounts to the wall, the shelf
    # catches a downward-moving bundle, and the rail catches outward travel.
    back = Box(
        back_thickness,
        holder_length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    shelf = Box(
        rail_inner_x + rail_thickness,
        holder_length,
        shelf_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    rail = Box(
        rail_thickness,
        holder_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((rail_inner_x, 0.0, 0.0))
    body = back + shelf + rail

    # A 4.4 mm through bore runs from the wall. It remains narrow for 2.6 mm,
    # then opens into a 9.0 mm front counterbore for the M4 pan head and driver.
    bore = Cylinder(
        screw_hole_diameter / 2.0,
        screw_seat_x + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90.0).translate((0.0, screw_y, screw_z))
    head_clearance = Cylinder(
        screw_head_clearance_diameter / 2.0,
        back_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90.0).translate((screw_seat_x, screw_y, screw_z))

    return body - bore - head_clearance
