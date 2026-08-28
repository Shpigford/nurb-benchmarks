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

    bundle_diameter: how thick the cable bundle is; sets the channel's width and depth
    cable_clearance: extra width in the channel so the bundle drops in without pinching
    wall_thickness: how thick each side wall of the channel is
    base_thickness: how much material sits under the cable, and how thick the tab is
    clip_length: how long the clip is along the cable
    tab_length: how far the screw tab sticks out sideways past the wall
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: how much is taken off the exposed outside edges
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter

    if channel_width < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a {channel_width:.1f}mm channel; "
            "under 2mm the walls fuse as they print. Raise it above "
            f"{2.0 - cable_clearance:.1f}",
            param="bundle_diameter",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed bore can "
            "hold open. Raise it above 2.0",
            param="screw_hole_width",
        )
    if tab_length - screw_hole_width < 2 * wall_thickness:
        reject(
            f"tab_length {tab_length} leaves "
            f"{(tab_length - screw_hole_width) / 2:.1f}mm of tab around the screw hole; "
            f"raise it above {screw_hole_width + 2 * wall_thickness:.1f}",
            param="tab_length",
        )

    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    corner = (Align.MIN, Align.MIN, Align.MIN)

    # Channel body, then the tab reaching out from the far wall, flush with the bottom.
    solid = Box(body_width, clip_length, height, align=corner)
    solid += Pos(body_width, 0, 0) * Box(tab_length, clip_length, base_thickness, align=corner)

    # The channel is cut through in Y and open at the top: the cutter overshoots both
    # so no face of it lands coplanar with a face of the body.
    solid -= Pos(wall_thickness, -1.0, base_thickness) * Box(
        channel_width, clip_length + 2.0, channel_depth + 1.0, align=corner
    )

    solid -= Pos(body_width + tab_length / 2, clip_length / 2, -1.0) * Cylinder(
        screw_hole_width / 2, base_thickness + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    if draft:
        return solid

    bed = solid.bounding_box().min.Z
    channel_min_x = wall_thickness
    channel_max_x = wall_thickness + channel_width
    tol = 1e-6

    def in_bed_plane(edge):
        # An edge lying flat in the bed face. A vertical corner that merely ends there
        # still chamfers: its facet stands square to the plate.
        return edge.bounding_box().max.Z < bed + tol

    def on_a_channel_face(point):
        on_inner_wall = (
            abs(point.X - channel_min_x) < tol or abs(point.X - channel_max_x) < tol
        ) and point.Z > base_thickness - tol
        on_floor = (
            abs(point.Z - base_thickness) < tol
            and channel_min_x - tol < point.X < channel_max_x + tol
        )
        return on_inner_wall or on_floor

    def bounds_the_channel(edge):
        # The cable's seat is mating geometry: floor, both inner walls and the mouth rim
        # stay square. A chamfer trims its neighbours where it ends too, so an edge that
        # merely lands on a channel face is out as well: that is what was shaving the
        # inner walls down from 8.0 x 12.0 at both ends of the clip.
        return any(on_a_channel_face(v.center()) for v in edge.vertices())

    def straight(edge):
        return str(edge.geom_type).endswith("LINE")

    inside = set(concave_edges(solid))
    keep = [
        e
        for e in solid.edges()
        if straight(e) and e not in inside and not in_bed_plane(e) and not bounds_the_channel(e)
    ]
    return polish(solid, keep, chamfer_size)
