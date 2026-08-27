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
    """Screw-down cable clip: an open-top channel the bundle lies in, and a flat tab beside it for one screw.

    bundle_diameter: how wide the cable bundle is; sets the channel's width and depth
    cable_clearance: extra room in the channel beyond the bundle, so it drops in
    wall_thickness: how thick each channel wall is
    base_thickness: how much floor sits under the cable, and how thick the screw tab is
    clip_length: how long the clip is along the cable
    tab_length: how far the screw tab sticks out beside the channel
    screw_hole_width: diameter of the screw hole through the tab
    """
    if bundle_diameter < 1.0:
        reject("bundle_diameter under 1mm leaves no channel to hold: raise it", param="bundle_diameter")
    if tab_length - screw_hole_width < 4.0:
        reject(
            f"screw_hole_width {screw_hole_width} leaves under 2mm of tab either side: "
            f"keep it below {tab_length - 4.0}",
            param="screw_hole_width",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = 2 * wall_thickness + channel_width
    body_height = base_thickness + channel_depth
    grounded = (Align.MIN, Align.CENTER, Align.MIN)

    body = Box(body_width, clip_length, body_height, align=grounded)
    # The cut runs past both ends and above the rim so no face of it lies on a face of the body.
    channel = Pos(wall_thickness, 0, base_thickness) * Box(
        channel_width, clip_length + 2.0, channel_depth + 1.0, align=grounded
    )
    tab = Pos(body_width, 0, 0) * Box(tab_length, clip_length, base_thickness, align=grounded)
    hole = Pos(body_width + tab_length / 2, 0, -1.0) * Cylinder(
        screw_hole_width / 2, base_thickness + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    clip = body + tab - channel - hole
    if draft:
        return clip

    # Polish the top perimeters only: every convex edge lying in a face that looks up.
    # Vertical corners stay sharp on purpose, so no corner has three chamfers meeting and
    # the part carries no corner-triangle slivers.
    eps = 1e-6
    bed = clip.bounding_box().min.Z
    concave = concave_edges(clip)

    def rim(e):
        bb = e.bounding_box()
        if e.geom_type != GeomType.LINE:
            return False  # the screw hole's rims and seam
        if bb.max.Z - bb.min.Z > eps or bb.max.Z <= bed + eps:
            return False  # vertical, or lying in the bed face
        if any(e.is_same(c) for c in concave):
            return False
        inside_channel = (
            bb.min.X >= wall_thickness - eps
            and bb.max.X <= wall_thickness + channel_width + eps
            and bb.min.Z >= base_thickness - eps
        )
        return not inside_channel  # the channel floor and mouth stay square

    return polish(clip, clip.edges().filter_by(rim), 1.0)
