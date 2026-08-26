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
    """A screw-down clip: an open-top channel holds the cable, a flat tab takes the screw.

    bundle_diameter: how wide the cable bundle is; the channel is cut 0.4 wider
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how long the clip runs along the cable
    tab_length: how far the mounting tab sticks out sideways
    screw_hole_width: the through-hole in the tab, sized for the mounting screw
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    body_height = base_thickness + channel_depth

    if screw_hole_width < 2.0:
        reject(
            "screw_hole_width under 2mm prints as a smear: raise it to 2 or more",
            param="screw_hole_width",
        )
    if tab_length < screw_hole_width + 2 * wall_thickness:
        reject(
            "tab_length leaves too little material around the screw hole: "
            f"raise it above {screw_hole_width + 2 * wall_thickness:.1f}",
            param="tab_length",
        )

    # Channel body sits with its bottom on Z=0, centred on X=0.
    body = Pos(0, 0, body_height / 2) * Box(body_width, clip_length, body_height)
    channel = Pos(0, 0, base_thickness + channel_depth / 2) * Box(
        channel_width, clip_length, channel_depth
    )
    body -= channel

    # Mounting tab extends in +X from the outside of the wall, flush with the bottom.
    tab_x = body_width / 2 + tab_length / 2
    tab = Pos(tab_x, 0, base_thickness / 2) * Box(tab_length, clip_length, base_thickness)
    hole = Pos(tab_x, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness
    )
    clip = body + tab - hole

    if draft:
        return clip

    # Chamfer only the outermost top edges, keeping the channel interior square
    # and staying clear of the tab-to-wall junction where a chamfer reads as
    # cosmetic polish in a structural corner.
    top = clip.bounding_box().max.Z
    outer = body_width / 2 - 1e-3
    keep = clip.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-3
        and (
            e.bounding_box().min.X < -outer or e.bounding_box().max.X > outer
        )
    )
    return polish(clip, keep, 1.0)
