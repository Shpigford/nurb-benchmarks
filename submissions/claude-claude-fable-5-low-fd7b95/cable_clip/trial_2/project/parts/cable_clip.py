from nurb import *


@part
def cable_clip(
    bundle_diameter=8.0,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    draft=False,
):
    """A screw-down clip holding a cable bundle in an open-top channel.

    bundle_diameter: how wide the cable bundle is across
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how long the clip runs along the cable
    tab_length: how far the mounting tab sticks out sideways
    screw_hole_width: how wide the screw hole in the tab is
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    if screw_hole_width < 2.0:
        reject(
            "screw_hole_width under 2mm prints as a smear: raise it to 2 or more",
            param="screw_hole_width",
        )

    # Channel body, centred on X=0, sitting on the bed.
    body = Pos(0, 0, height / 2) * Box(body_width, clip_length, height)
    channel = Pos(0, 0, base_thickness + channel_depth / 2 + 0.5) * Box(
        channel_width, clip_length, channel_depth + 1.0
    )
    body -= channel

    # Mounting tab off the +X wall, flush with the bottom.
    tab = Pos(body_width / 2 + tab_length / 2, 0, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    hole = Pos(body_width / 2 + tab_length / 2, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 1.0
    )
    clip = body + tab - hole

    if draft:
        return clip

    # Polish: exposed convex edges only. Keep the bed-contact bottom, the
    # fit-critical channel interior, and the screw hole rim untouched.
    bed = clip.bounding_box().min.Z
    concave = set(concave_edges(clip))
    keep = clip.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e not in concave
        and e.geom_type != GeomType.CIRCLE
        and not (
            abs(e.bounding_box().max.X) < channel_width / 2 + 1e-6
            and e.bounding_box().min.Z > base_thickness - 1e-6
        )
        and not (
            e.bounding_box().max.Z - e.bounding_box().min.Z > 1e-6
        )
    )
    return polish(clip, keep, 1.0)
