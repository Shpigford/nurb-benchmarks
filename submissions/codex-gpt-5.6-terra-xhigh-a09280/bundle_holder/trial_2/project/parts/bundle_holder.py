from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A one-screw wall cradle for a horizontal cable bundle.

    bundle_diameter: measured diameter of the cable bundle held in the open-top cradle.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than zero", param="bundle_diameter")

    # The channel deliberately has 0.4 mm of free space on each constrained side.
    # It is open above so the bundle can be installed from the front/top, while the
    # grounded rail and floor positively stop the required outward and downward moves.
    back_thickness = 3.0
    holder_length = 14.0
    floor_thickness = 2.0
    side_clearance = 0.4
    front_rail_thickness = 2.8

    channel_width = bundle_diameter + 2.0 * side_clearance
    rail_inner_x = back_thickness + channel_width
    total_depth = rail_inner_x + front_rail_thickness

    rail_height = floor_thickness + bundle_diameter

    # Keep the pan-head centre above the cable.  These dimensions also leave a 0.4 mm
    # rim around the virtual 8.4 mm head at the top of the back plate.
    screw_center_z = bundle_diameter + 7.4
    back_height = bundle_diameter + 12.0
    screw_hole_diameter = 4.4

    back = Box(
        back_thickness,
        holder_length,
        back_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    floor = Box(
        total_depth,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    front_rail = Box(
        front_rail_thickness,
        holder_length,
        rail_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((rail_inner_x, 0.0, 0.0))

    body = back + floor + front_rail

    # The bore opens on the wall face (minimum X). Its 3 mm-long shank passage
    # leaves an annular seat for the M4 pan head on the outward face of the back.
    bore = Cylinder(
        screw_hole_diameter / 2.0,
        back_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90.0).translate((0.0, 0.0, screw_center_z))

    return body - bore
