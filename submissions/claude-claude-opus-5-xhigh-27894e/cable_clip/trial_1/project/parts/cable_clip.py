from nurb import *

# Three 1mm chamfers meeting at a convex corner leave a 0.87mm2 triangle, which the
# sliver rule fires on. 1.2mm puts that same corner at 1.25mm2 and keeps the part clean.
CHAMFER = 1.2


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    draft=False,
):
    """A screw-down clip holding a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra width in the channel so the bundle drops in
    wall_thickness: how thick each of the two channel walls is
    base_thickness: how much material sits under the cable, and how thick the tab is
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out sideways
    screw_hole_width: across the screw hole in the tab
    """
    if bundle_diameter < 2.0:
        reject(
            "bundle_diameter %.2f leaves a channel too narrow to print: "
            "raise it above 2.0" % bundle_diameter,
            param="bundle_diameter",
        )
    if screw_hole_width + 2 * CHAMFER >= min(tab_length, clip_length):
        reject(
            "screw_hole_width %.2f leaves no material around the bore: "
            "widen the tab or shrink the hole" % screw_hole_width,
            param="screw_hole_width",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    # The channel body sits on the bed with its left wall on x = 0.
    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, clip_length, height)

    # Open top, and the channel runs the full length along Y, so the cut overshoots both.
    over = 2.0
    channel = Pos(
        wall_thickness + channel_width / 2,
        0,
        base_thickness + (channel_depth + over) / 2,
    ) * Box(channel_width, clip_length + 2 * over, channel_depth + over)

    # Mounting tab off the right wall, flush with the bottom, screwed down through a
    # vertical bore on its centre.
    tab_centre = body_width + tab_length / 2
    tab = Pos(tab_centre, 0, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    screw = Pos(tab_centre, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + over
    )

    shape = (body + tab) - channel - screw

    if draft:
        return shape

    # Name what must stay sharp, then let `polish` chamfer whatever the kernel takes.
    tol = 1e-6
    bed = shape.bounding_box().min.Z
    inner_left = wall_thickness
    inner_right = wall_thickness + channel_width

    def on_channel(point):
        # The three faces the cable bears on: two inner walls and the floor between
        # them.
        x, _, z = point.X, point.Y, point.Z
        if z > base_thickness - tol and (
            abs(x - inner_left) < tol or abs(x - inner_right) < tol
        ):
            return True
        return (
            abs(z - base_thickness) < tol
            and x > inner_left - tol
            and x < inner_right + tol
        )

    def in_channel(edge):
        # The channel is the mating surface: its walls and floor stay square, so the
        # cable seats on flat faces at their full nominal size. An edge that merely
        # *ends* on one of them, like the rim across the top of a wall, would still
        # nick the corner off it, so touching at a vertex is enough to exclude.
        return any(on_channel(v.center()) for v in edge.vertices())

    concave = set(concave_edges(shape))
    keep = shape.edges().filter_by(
        # Edges lying in the bed face buy nothing; a vertical corner that merely ends
        # there keeps its chamfer.
        lambda e: e.bounding_box().max.Z > bed + tol
        and e not in concave
        and e.geom_type != GeomType.CIRCLE  # the bore stays full width top to bottom
        and not in_channel(e)
    )
    return polish(shape, keep, CHAMFER)
