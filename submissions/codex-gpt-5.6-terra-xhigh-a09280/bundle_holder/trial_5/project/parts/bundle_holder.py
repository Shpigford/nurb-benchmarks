from nurb import *


@part
def bundle_holder(bundle_diameter: float = measured("bundle_diameter")):
    """A compact, wall-mounted channel for a horizontal cable bundle.

    bundle_diameter: measured diameter of the cable bundle held in the channel
    """
    # The channel is deliberately open above: it prints without bridges while the
    # floor and front rail independently stop downward and outward movement.
    bundle_clearance = 0.6
    wall_thickness = 3.0
    floor_thickness = 2.4
    holder_length = 16.0
    front_rail_thickness = 2.2
    screw_hole_diameter = 4.4
    screw_head_diameter = 8.4

    channel_width = bundle_diameter + bundle_clearance
    cable_center_z = floor_thickness + channel_width / 2
    front_rail_height = bundle_diameter / 2 + bundle_clearance

    # Keeping the pan head just clear above the bundle leaves the entire channel
    # unobstructed, including at the screw's Y position.
    screw_center_z = (
        cable_center_z + bundle_diameter / 2 + screw_head_diameter / 2 + 0.5
    )
    # The wall surrounds the full 8.4 mm pan-head footprint at its seat.
    wall_height = screw_center_z + screw_head_diameter / 2 + 1.0

    wall = Box(
        wall_thickness,
        holder_length,
        wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        wall_thickness + channel_width + front_rail_thickness,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    front_rail = Box(
        front_rail_thickness,
        holder_length,
        front_rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness + channel_width, 0, floor_thickness))

    body = wall + floor + front_rail

    # The bore begins at the wall face. The pan head lands on the forward face of
    # the 3 mm wall; above it is open air, so the head and driver have clear access.
    screw_bore = Cylinder(
        screw_hole_diameter / 2,
        wall_thickness + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90).translate((-0.1, holder_length / 2, screw_center_z))

    return body - screw_bore
