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
    chamfer_size=1.0,
    draft=False,
):
    """A screw-down clip holding a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra channel width so the bundle drops in without forcing
    wall_thickness: how thick each of the two channel walls is
    base_thickness: how much material sits under the cable, and how thick the tab is
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out past the wall
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: how much is taken off the outside edges
    """
    if bundle_diameter <= 0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves no channel: it is the width and "
            "the depth of the cable slot, so raise it above 0",
            param="bundle_diameter",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed bore can "
            "hold open: raise it to 2 or more",
            param="screw_hole_width",
        )
    if tab_length < screw_hole_width + 2 * wall_thickness:
        reject(
            f"tab_length {tab_length} leaves under {wall_thickness}mm of tab around a "
            f"{screw_hole_width}mm hole: raise it above "
            f"{screw_hole_width + 2 * wall_thickness}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    # One extruded profile: walls and base in a block, tab flush with the bed beside it.
    body = Pos(body_width / 2, clip_length / 2, height / 2) * Box(
        body_width, clip_length, height
    )
    tab = Pos(body_width + tab_length / 2, clip_length / 2, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    solid = body + tab

    # Open at both ends, so the cut runs past y=0 and y=clip_length.
    solid -= Pos(
        body_width / 2, clip_length / 2, base_thickness + channel_depth / 2
    ) * Box(channel_width, clip_length + 2 * wall_thickness, channel_depth)

    solid -= Pos(body_width + tab_length / 2, clip_length / 2, base_thickness / 2) * (
        Cylinder(screw_hole_width / 2, 2 * base_thickness)
    )

    if draft:
        return solid

    bed = solid.bounding_box().min.Z
    concave = set(concave_edges(solid))
    hole_x = body_width + tab_length / 2
    hole_y = clip_length / 2
    tol = 1e-6

    # The channel is what the cable drops into: no lead-in, no rounded rim, so its
    # floor stays one flat face the full width and its walls stay square. An edge that
    # merely touches a channel surface counts, because chamfering it clips the corner
    # off that surface.
    def touches_the_channel(e):
        bb = e.bounding_box()
        return (
            bb.max.X > wall_thickness - tol
            and bb.min.X < wall_thickness + channel_width + tol
            and bb.max.Z > base_thickness - tol
        )

    # The screw seats on this rim, so it stays sharp: a chamfer here feathers the 3mm
    # tab down under what the nozzle lays.
    def at_the_screw_hole(e):
        bb = e.bounding_box()
        return (
            bb.min.X > hole_x - screw_hole_width / 2 - tol
            and bb.max.X < hole_x + screw_hole_width / 2 + tol
            and bb.min.Y > hole_y - screw_hole_width / 2 - tol
            and bb.max.Y < hole_y + screw_hole_width / 2 + tol
        )

    # Horizontal edges only. A vertical corner would carry a third chamfer into the
    # top corners, and three of them meeting leave a sub-1mm2 sliver facet.
    def upright(e):
        bb = e.bounding_box()
        return bb.max.Z - bb.min.Z > tol

    keep = [
        e
        for e in solid.edges()
        if e not in concave
        and e.bounding_box().min.Z > bed + tol
        and not upright(e)
        and not touches_the_channel(e)
        and not at_the_screw_hole(e)
    ]
    return polish(solid, keep, chamfer_size)
