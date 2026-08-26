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
    """
    bundle_diameter: how wide the cable bundle is; the channel is 0.4 wider and this deep
    wall_thickness: how thick each channel wall is
    base_thickness: how thick the floor under the cable is, and the mounting tab
    length: how long the clip is along the cable
    tab_length: how far the mounting tab sticks out from the wall
    screw_hole_width: diameter of the screw hole in the tab
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    if tab_length < screw_hole_width + 2.0:
        reject("tab_length is too short to carry the screw hole", param="tab_length")

    body = Pos(body_width / 2, length / 2, height / 2) * Box(body_width, length, height)
    channel = Pos(body_width / 2, length / 2, base_thickness + channel_depth / 2) * Box(
        channel_width, length, channel_depth
    )
    body = body - channel
    tab = Pos(body_width + tab_length / 2, length / 2, base_thickness / 2) * Box(
        tab_length, length, base_thickness
    )
    body = body + tab
    hole = Pos(body_width + tab_length / 2, length / 2, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 2
    )
    body = body - hole
    if draft:
        return body

    # Polish only the three outer top rims that run along the cable: the channel mouth,
    # the bed edges and the screw hole stay sharp, and a vertical corner chamfer would
    # run into the tab and leave a crease.
    concave = set(concave_edges(body))
    inner_lo = body_width / 2 - channel_width / 2
    inner_hi = body_width / 2 + channel_width / 2

    def exposed(e):
        bb = e.bounding_box()
        if e in concave or e.geom_type != GeomType.LINE:
            return False
        along_y = bb.max.Y - bb.min.Y > length - 1e-6
        outer = bb.min.X < inner_lo - 1e-6 or bb.max.X > inner_hi + 1e-6
        top = bb.min.Z > base_thickness - 1e-6 and bb.max.Z - bb.min.Z < 1e-6
        return along_y and outer and top

    keep = body.edges().filter_by(exposed)
    return polish(body, keep, 1.0)
