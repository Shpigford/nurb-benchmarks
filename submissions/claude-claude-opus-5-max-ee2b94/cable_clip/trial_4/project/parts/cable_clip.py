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
    """An open-top channel that traps a cable bundle, screwed down through a side tab.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra channel width so the bundle drops in without forcing
    wall_thickness: how thick each of the two channel walls is
    base_thickness: how much material sits under the channel, and how thick the tab is
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out past the wall
    screw_hole_width: how wide the screw hole through the tab is
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    around_hole = min(tab_length, clip_length) / 2 - screw_hole_width / 2
    if around_hole < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} leaves {around_hole:.2f}mm of tab "
            f"around the bore; keep it under "
            f"{min(tab_length, clip_length) - 4.0:.1f}",
            param="screw_hole_width",
        )

    # Body and tab are both grounded prisms, so the whole part prints as it sits.
    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, clip_length, height)
    tab = Pos(body_width + tab_length / 2, 0, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    # The channel is cut open-topped and runs out both ends of the part.
    channel = Pos(body_width / 2, 0, base_thickness + channel_depth) * Box(
        channel_width, clip_length + 2, 2 * channel_depth
    )
    hole = Pos(body_width + tab_length / 2, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, 3 * base_thickness
    )
    clip = (body + tab) - channel - hole
    if draft:
        return clip

    bed = clip.bounding_box().min.Z
    tol = 1e-6
    channel_far = wall_thickness + channel_width
    concave = [e.center() for e in concave_edges(clip)]

    def exposed(e):
        b = e.bounding_box()
        # Lies in the bed-contact face: a chamfer there buys nothing.
        if b.max.Z < bed + tol:
            return False
        # The channel is the fit: floor, inner walls and mouth all stay square.
        if (
            b.min.X > wall_thickness - tol
            and b.max.X < channel_far + tol
            and b.min.Z > base_thickness - tol
        ):
            return False
        # The screw hole's rim is what the screw head bears on.
        if e.geom_type != GeomType.LINE:
            return False
        # Cross-part top edges stay square. Chamfering them would put a third
        # chamfer on every top corner, and three meeting is what leaves a sliver.
        if b.max.Y - b.min.Y < tol and b.max.Z - b.min.Z < tol:
            return False
        c = e.center()
        return not any((c - p).length < 1e-4 for p in concave)

    return polish(clip, clip.edges().filter_by(exposed), 1.0)
