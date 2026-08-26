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
    chamfer_size=1.2,
    draft=False,
):
    """A screw-down clip that traps a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra width in the channel so the bundle drops in
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab sticks out sideways
    screw_hole_width: the through-hole in the tab
    chamfer_size: the bevel on the exposed edges
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be positive", param="bundle_diameter")
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} prints as a smear: raise it above 2.0",
            param="screw_hole_width",
        )
    if tab_length <= screw_hole_width:
        reject(
            f"tab_length {tab_length} leaves no material around a "
            f"{screw_hole_width}mm hole: raise it above {screw_hole_width + 4:.1f}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    block_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    body = Pos(block_width / 2, clip_length / 2, height / 2) * Box(
        block_width, clip_length, height
    )
    tab = Pos(
        block_width + tab_length / 2, clip_length / 2, base_thickness / 2
    ) * Box(tab_length, clip_length, base_thickness)
    solid = body + tab

    channel = Pos(
        block_width / 2, clip_length / 2, base_thickness + channel_depth / 2
    ) * Box(channel_width, clip_length, channel_depth)
    solid -= channel

    hole = Pos(block_width + tab_length / 2, clip_length / 2, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness * 2
    )
    solid -= hole

    if draft:
        return solid

    bed = solid.bounding_box().min.Z
    concave = set(concave_edges(solid))
    channel_lo = wall_thickness - 1e-6
    channel_hi = wall_thickness + channel_width + 1e-6

    def keep(e):
        bb = e.bounding_box()
        if bb.max.Z <= bed + 1e-6:
            return False
        if e in concave:
            return False
        # nothing inside the channel gets touched: the floor stays flat and the
        # mouth stays square
        if bb.min.X > channel_lo and bb.max.X < channel_hi:
            return False
        # the screw bore stays square: a chamfered mouth thins the tab
        if e.geom_type != GeomType.LINE:
            return False
        return True

    return polish(solid, solid.edges().filter_by(keep), chamfer_size)
