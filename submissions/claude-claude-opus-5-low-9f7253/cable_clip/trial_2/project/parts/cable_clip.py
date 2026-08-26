from nurb import *


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
    cable_clearance: extra width in the channel so the bundle drops in
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab sticks out sideways
    screw_hole_width: diameter of the through-hole for the mounting screw
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    if screw_hole_width + 2.0 > tab_length:
        reject(
            f"tab_length {tab_length} leaves under 1mm of material beside a "
            f"{screw_hole_width}mm hole: raise it above {screw_hole_width + 2.0}",
            param="tab_length",
        )

    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, clip_length, height)
    body -= Pos(body_width / 2, 0, base_thickness + channel_depth / 2) * Box(
        channel_width, clip_length + 2, channel_depth
    )
    body += Pos(body_width + tab_length / 2, 0, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    hole_x = body_width + tab_length / 2
    body -= Pos(hole_x, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 2
    )

    if draft:
        return body

    channel_min = body_width / 2 - channel_width / 2
    channel_max = body_width / 2 + channel_width / 2

    def vertical_corner(e):
        bb = e.bounding_box()
        if bb.max.Z - bb.min.Z < 1.0:
            return False
        if bb.max.X - bb.min.X > 1e-6 or bb.max.Y - bb.min.Y > 1e-6:
            return False
        # Nothing inside the channel, and nothing around the screw bore.
        if channel_min - 1e-6 < bb.min.X < channel_max + 1e-6:
            return False
        if abs(bb.min.X - hole_x) < screw_hole_width:
            return False
        return True

    concave = {
        (round(e.center().X, 3), round(e.center().Y, 3), round(e.center().Z, 3))
        for e in concave_edges(body)
    }

    def keepable(e):
        c = (round(e.center().X, 3), round(e.center().Y, 3), round(e.center().Z, 3))
        return vertical_corner(e) and c not in concave

    return polish(body, body.edges().filter_by(keepable), 1.0)
