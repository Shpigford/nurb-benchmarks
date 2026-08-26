from nurb import *


@part
def cable_clip(
    bundle_diameter=8.0,
    wall_thickness=2.4,
    base_thickness=3.0,
    length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    draft=False,
):
    """Screw-down clip: an open-top channel for a cable bundle with a flat mounting tab.

    bundle_diameter: how wide the cable bundle is; sets the channel width and depth
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable (and the tab thickness)
    length: how long the clip is along the cable
    tab_length: how far the mounting tab sticks out from the channel wall
    screw_hole_width: diameter of the screw hole in the tab
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    body = Box(body_width, length, height, align=(Align.MIN, Align.MIN, Align.MIN))
    channel = Box(channel_width, length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN))
    body -= Pos(wall_thickness, 0, base_thickness) * channel

    tab = Box(tab_length, length, base_thickness, align=(Align.MIN, Align.MIN, Align.MIN))
    body += Pos(body_width, 0, 0) * tab
    hole = Cylinder(screw_hole_width / 2, base_thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(body_width + tab_length / 2, length / 2, 0) * hole

    if draft:
        return body
    # Chamfer exposed convex edges only: never the bed face, never inside the channel,
    # never the screw hole rim.
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > 0
        and e not in concave
        and e.geom_type != GeomType.CIRCLE
        and abs(e.bounding_box().max.Z - e.bounding_box().min.Z) < 0.01
        and not (
            wall_thickness - 0.01 < e.bounding_box().min.X
            and e.bounding_box().max.X < wall_thickness + channel_width + 0.01
            and e.bounding_box().min.Z > base_thickness - 0.01
        )
        and e.geom_type != GeomType.CIRCLE
    )
    return polish(body, keep, 1.0)
