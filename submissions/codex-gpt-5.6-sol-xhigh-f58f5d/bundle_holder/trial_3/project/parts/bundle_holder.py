from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    draft=False,
):
    """Hold a horizontal cable bundle against a wall with one M4 screw.

    bundle_diameter: measured width across the cable bundle
    """
    clearance = 0.4
    bundle_space = bundle_diameter + clearance

    length = 12.0
    wall_thickness = 2.4
    back_thickness = 3.0

    # The open channel gives the bundle radial clearance while retaining it in
    # the two load directions: the floor blocks -Z and the front wall blocks +X.
    channel_front_x = back_thickness + bundle_space
    front_height = wall_thickness + 0.85 * bundle_space

    # Keep the pan head wholly above the retained bundle. The 3.0 mm back gives
    # the screw more than the required 2.4 mm of bearing length before its seat.
    head_radius = 4.2
    screw_center_z = wall_thickness + bundle_space + head_radius + 0.7
    back_height = screw_center_z + head_radius + 0.8

    back = Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        bundle_space + wall_thickness,
        length,
        wall_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((back_thickness, 0, 0))
    front = Box(
        wall_thickness,
        length,
        front_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((channel_front_x, 0, 0))

    holder = back + floor + front

    # A 4.5 mm square rotated 45 degrees contains the required 4.4 mm bore.
    # Its diamond section gives the horizontal printed hole self-supporting
    # 45-degree ceilings while retaining a continuous axis along X.
    screw_hole = Box(
        back_thickness + 0.4,
        4.5,
        4.5,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    ).rotate(Axis.X, 45).translate((-0.2, length / 2, screw_center_z))
    holder = holder - screw_hole

    if draft:
        return holder

    # Dress the long exposed top edges while preserving the bed, wall-mating
    # back, channel floor, and all screw/bundle fit surfaces.
    top_edges = holder.edges().filter_by(
        lambda edge: edge.bounding_box().size.Y > length - 0.01
        and edge.bounding_box().min.X > 0.01
        and (
            abs(edge.bounding_box().min.Z - back_height) < 0.01
            or abs(edge.bounding_box().min.Z - front_height) < 0.01
        )
    )
    return polish(holder, top_edges, 1.0)
