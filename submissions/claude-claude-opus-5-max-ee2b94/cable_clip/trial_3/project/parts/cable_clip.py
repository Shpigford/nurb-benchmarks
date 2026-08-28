from nurb import *

TOL = 1e-6


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
    """A screw-down clip that traps a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra channel width so the bundle drops in without forcing
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how far the clip runs along the cable
    tab_length: how far the mounting tab sticks out past the wall
    screw_hole_width: diameter of the screw hole through the tab
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    if channel_width < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a {channel_width:.1f}mm channel, "
            f"narrower than a nozzle can cut: raise it above {2.0 - cable_clearance}",
            param="bundle_diameter",
        )
    if tab_length < screw_hole_width + 2 * wall_thickness:
        reject(
            f"tab_length {tab_length} cannot carry a {screw_hole_width}mm hole with wall "
            f"around it: raise it above {screw_hole_width + 2 * wall_thickness}",
            param="tab_length",
        )

    # Channel block: two walls on a solid base, open along the whole of Y.
    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, clip_length, height)
    channel = Pos(
        wall_thickness + channel_width / 2, 0, base_thickness + (channel_depth + 2) / 2
    ) * Box(channel_width, clip_length + 2, channel_depth + 2)
    body = body - channel

    # Mounting tab, flush with the bed. It reaches a wall's width back into the body so
    # the union is an overlap rather than two faces kissing.
    tab_reach = tab_length + wall_thickness
    body = body + Pos(
        body_width + tab_length - tab_reach / 2, 0, base_thickness / 2
    ) * Box(tab_reach, clip_length, base_thickness)

    hole_center = body_width + tab_length / 2
    body = body - Pos(hole_center, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 2
    )

    if draft:
        return body

    bed = body.bounding_box().min.Z
    inner_lo = wall_thickness - TOL
    inner_hi = wall_thickness + channel_width + TOL

    def outside_the_channel(e):
        bb = e.bounding_box()
        return not (
            bb.min.X >= inner_lo and bb.max.X <= inner_hi and bb.max.Z > base_thickness - TOL
        )

    def off_the_channel_rim(e):
        # A chamfer across the end of a wall top runs its facet down into the channel
        # wall. The wall ends stay sharp so the channel stays a clean rectangle.
        bb = e.bounding_box()
        return not (bb.min.Z > height - TOL and bb.max.X - bb.min.X > TOL)

    concave = set(concave_edges(body))
    bore = {e for f in body.faces().filter_by(GeomType.CYLINDER) for e in f.edges()}
    keep = [
        e
        for e in body.edges()
        if e not in concave
        and e not in bore  # the screw head bears on a flat tab
        and e.bounding_box().max.Z > bed + TOL  # nothing lying in the bed face
        and outside_the_channel(e)  # nothing inside the cable channel
        and off_the_channel_rim(e)  # nothing that reaches into the channel wall
    ]
    # 1.2 rather than the house 1.0: three chamfers meet at each outer tab corner, and
    # at 1.0 the facet they leave is 0.87mm2, under what a nozzle lays cleanly.
    return polish(body, keep, 1.2)
