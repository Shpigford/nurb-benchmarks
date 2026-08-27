from nurb import *


@part
def bundle_holder(bundle_diameter: float = 8.0):
    """Wall-mounted cradle for a horizontal cable bundle.

    bundle_diameter: measured width of the cable bundle.
    """
    bundle_clearance = 0.8
    channel_width = bundle_diameter + bundle_clearance

    holder_length = 12.0
    back_thickness = 2.8
    floor_thickness = 2.4
    front_thickness = 2.0

    screw_hole_radius = 2.2
    screw_height = floor_thickness + bundle_diameter + 5.4

    front_inside = back_thickness + channel_width
    holder_depth = front_inside + front_thickness
    front_height = floor_thickness + 0.85 * channel_width
    back_height = screw_height + 4.0

    back = Box(
        back_thickness,
        holder_length,
        back_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    floor = Box(
        holder_depth,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    front = Pos(front_inside, 0, 0) * Box(
        front_thickness,
        holder_length,
        front_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    holder = back + floor + front

    # The horizontal bore starts just behind the wall face so it opens cleanly.
    screw_bore = Pos(-0.2, 0, screw_height) * Rot(0, 90, 0) * Cylinder(
        screw_hole_radius,
        back_thickness + 0.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    holder = holder - screw_bore

    # Soften only the exposed outer lip; the wall face, cradle contacts, bed,
    # and screw seat stay dimensionally exact.
    outer_lip_edge = holder.edges().filter_by(
        lambda edge: (
            abs(edge.bounding_box().min.X - holder_depth) < 0.01
            and abs(edge.bounding_box().min.Z - front_height) < 0.01
        )
    )
    return polish(holder, outer_lip_edge, 1.0)
