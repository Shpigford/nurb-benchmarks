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
    screw_hole_width: the through-hole for the mounting screw
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    if channel_width < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a channel under 2mm wide: raise it",
            param="bundle_diameter",
        )

    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    # Body sits x: 0..body_width, y: 0..clip_length, z: 0..height.
    body = Pos(body_width / 2, clip_length / 2, height / 2) * Box(
        body_width, clip_length, height
    )

    channel = Pos(
        body_width / 2,
        clip_length / 2,
        base_thickness + channel_depth / 2 + 1.0,
    ) * Box(channel_width, clip_length + 2.0, channel_depth + 2.0)
    body = body - channel

    tab = Pos(
        body_width + tab_length / 2, clip_length / 2, base_thickness / 2
    ) * Box(tab_length, clip_length, base_thickness)
    body = body + tab

    hole_center = body_width + tab_length / 2
    body = body - (
        Pos(hole_center, clip_length / 2, base_thickness / 2)
        * Cylinder(screw_hole_width / 2, base_thickness + 2.0)
    )

    if draft:
        return body

    bed = body.bounding_box().min.Z
    channel_x0 = wall_thickness
    channel_x1 = wall_thickness + channel_width

    def keepable(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 1e-6:
            return False
        # Leave the channel alone: it is the surface the bundle beds against.
        if (
            bb.min.X > channel_x0 - 1e-6
            and bb.max.X < channel_x1 + 1e-6
            and bb.min.Z > base_thickness - 1e-6
        ):
            return False
        # The wall tops keep their short end edges square: chamfering them too
        # collides with the long top chamfer and leaves sliver facets.
        if bb.min.Z > height - 1e-6 and bb.max.X - bb.min.X > 1e-6:
            return False
        # The screw bore keeps its rim square: a chamfer there thins the tab.
        if bb.min.X > hole_center - screw_hole_width and bb.max.X < hole_center + screw_hole_width:
            return False
        return True

    keep = body.edges().filter_by(keepable)
    concave = set(concave_edges(body))
    keep = [e for e in keep if e not in concave]
    return polish(body, keep, 1.0)
