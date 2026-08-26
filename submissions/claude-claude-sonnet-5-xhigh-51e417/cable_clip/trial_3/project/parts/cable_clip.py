from nurb import *

MIN = Align.MIN
CENTER = Align.CENTER


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    wall=2.4,
    base=3.0,
    part_length=12.0,
    tab_length=10.0,
    hole_diameter=4.2,
    draft=False,
):
    """bundle_diameter: the cable bundle's diameter, across
    wall: channel wall thickness on each side
    base: solid floor thickness under the channel
    part_length: length of the clip along the cable (Y)
    tab_length: how far the mounting tab extends past the wall
    hole_diameter: the mounting screw's through-hole diameter
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = 2 * wall + channel_width
    body_height = base + channel_depth
    tab_thickness = base

    body = Box(body_width, part_length, body_height, align=(MIN, MIN, MIN))
    channel = Pos(wall, 0, base) * Box(
        channel_width, part_length, channel_depth, align=(MIN, MIN, MIN)
    )
    tab = Pos(body_width, 0, 0) * Box(
        tab_length, part_length, tab_thickness, align=(MIN, MIN, MIN)
    )
    hole = Pos(body_width + tab_length / 2, part_length / 2, -1) * Cylinder(
        hole_diameter / 2, tab_thickness + 2, align=(CENTER, CENTER, MIN)
    )

    solid = (body - channel) + tab
    shape = solid - hole
    if draft:
        return shape

    bed = shape.bounding_box().min.Z
    channel_lo = wall
    channel_hi = wall + channel_width
    concave = concave_edges(shape)
    hole_edges = set(new_edges(solid, combined=shape))

    def vertical(box):
        return box.max.X - box.min.X < 1e-6 and box.max.Y - box.min.Y < 1e-6

    def exposed(e):
        box = e.bounding_box()
        if box.max.Z <= bed + 1e-6:
            return False
        if box.min.X >= channel_lo - 1e-6 and box.max.X <= channel_hi + 1e-6:
            return False
        if e in concave or e in hole_edges:
            return False
        if vertical(box):
            # A vertical corner chamfer here meets two others at every outer
            # corner, since none of the three is excluded by the tests above,
            # and all three landing together leaves a sub-mm2 corner triangle.
            # Skipping the vertical member keeps every corner to a plain miter.
            return False
        return True

    keep = shape.edges().filter_by(exposed)
    return polish(shape, keep, 1.0)
