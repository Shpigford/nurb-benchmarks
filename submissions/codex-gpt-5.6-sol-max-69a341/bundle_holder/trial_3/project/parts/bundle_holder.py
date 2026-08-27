from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter")):
    """Wall-mounted horizontal cable-bundle holder.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    clearance = 0.4
    wall_thickness = 3.0
    holding_thickness = 2.4
    holder_length = 12.0
    screw_hole_width = 4.4
    screw_head_width = 8.4

    channel_width = bundle_diameter + clearance
    bundle_center_height = holding_thickness + channel_width / 2
    front_wall_x = wall_thickness + channel_width
    front_wall_height = holding_thickness + channel_width * 0.72

    # Keep the installed screw head completely above the retained bundle.
    screw_center_height = (
        bundle_center_height
        + bundle_diameter / 2
        + 1.2
        + screw_head_width / 2
    )
    back_height = screw_center_height + screw_hole_width / 2 + holding_thickness

    minimum = (Align.MIN, Align.MIN, Align.MIN)
    back = Box(wall_thickness, holder_length, back_height, align=minimum)
    floor = Box(
        front_wall_x + holding_thickness,
        holder_length,
        holding_thickness,
        align=minimum,
    )
    front = Pos(front_wall_x, 0, 0) * Box(
        holding_thickness,
        holder_length,
        front_wall_height,
        align=minimum,
    )

    body = back + floor + front

    # A 45-degree diamond is support-free on its side and contains a full
    # 4.4 mm circular clearance bore.  It extends through both faces.
    root_two = 2.0 ** 0.5
    diamond_radius = screw_hole_width / root_two + 0.1
    diamond_side = diamond_radius * root_two
    screw_passage = Box(
        wall_thickness + 2.0,
        diamond_side,
        diamond_side,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    screw_passage = screw_passage.rotate(Axis.X, 45)
    screw_passage = Pos(
        wall_thickness / 2,
        holder_length / 2,
        screw_center_height,
    ) * screw_passage

    return body - screw_passage
