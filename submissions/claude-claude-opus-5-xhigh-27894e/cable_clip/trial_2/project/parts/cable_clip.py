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
    chamfer_size=1.2,
    draft=False,
):
    """A screw-down clip: the cable bundle drops into an open channel from above.

    bundle_diameter: how thick the cable bundle is, measured across the taped bundle
    cable_clearance: extra channel width so the bundle drops in without being forced
    wall_thickness: how thick each of the two channel walls is
    base_thickness: material under the channel, and the thickness of the screw tab
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out past the wall
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: how big the chamfer is on the exposed outside edges
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter has to be a real cable size", param="bundle_diameter")
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under 2mm, where a printed bore "
            "closes up: raise it to 2 or more, or drill it",
            param="screw_hole_width",
        )
    if tab_length < screw_hole_width + 4.0:
        reject(
            f"tab_length {tab_length} leaves under 2mm of tab around a "
            f"{screw_hole_width}mm hole: raise it above {screw_hole_width + 4.0}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    hole_x = body_width + tab_length / 2

    # The channel cuts out through the top and past both ends, so it opens on three
    # sides and its floor stays one flat face the full width.
    body = Box(
        body_width, clip_length, height, align=(Align.MIN, Align.CENTER, Align.MIN)
    )
    channel = Pos(wall_thickness, 0, base_thickness) * Box(
        channel_width,
        clip_length + 2,
        channel_depth + 1,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    # The tab is the same slab as the base, carried on past the wall: bottoms flush,
    # and its top lands on the channel floor plane.
    tab = Pos(body_width, 0, 0) * Box(
        tab_length,
        clip_length,
        base_thickness,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    screw = Pos(hole_x, 0, -1) * Cylinder(
        screw_hole_width / 2,
        base_thickness + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    solid = (body + tab) - channel - screw
    if draft:
        return solid

    bed = solid.bounding_box().min.Z
    channel_min = wall_thickness - TOL
    channel_max = wall_thickness + channel_width + TOL

    def span(edge):
        b = edge.bounding_box()
        return (
            round(b.min.X, 4),
            round(b.min.Y, 4),
            round(b.min.Z, 4),
            round(b.max.X, 4),
            round(b.max.Y, 4),
            round(b.max.Z, 4),
        )

    concave = {span(e) for e in concave_edges(solid)}

    def exposed(edge):
        box = edge.bounding_box()
        if span(edge) in concave:
            return False  # a chamfer on an inside corner is a feather edge
        if box.max.Z <= bed + TOL:
            return False  # lies in the bed face
        if box.max.X >= channel_min and box.min.X <= channel_max:
            return False  # anything reaching the channel: a lead-in at its mouth
        if edge.geom_type == GeomType.CIRCLE:
            return False  # the bore stays full width for the whole screw
        return True

    return polish(solid, solid.edges().filter_by(exposed), chamfer_size)
