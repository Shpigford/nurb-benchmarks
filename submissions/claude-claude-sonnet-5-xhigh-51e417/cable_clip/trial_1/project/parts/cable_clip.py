from nurb import *
from build123d import Align, GeomType


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    wall_thickness=2.4,
    base_thickness=3.0,
    tab_length=10.0,
    hole_diameter=4.2,
    draft=False,
):
    """Screw-down cable clip: an open-top channel over a flat mounting tab.

    bundle_diameter: the cable bundle's diameter, sets the channel's width and depth
    wall_thickness: thickness of the two walls that flank the channel
    base_thickness: solid material under the channel floor, and the tab's thickness
    tab_length: how far the mounting tab extends past the channel wall
    hole_diameter: diameter of the screw clearance hole through the tab
    """
    if bundle_diameter <= 0:
        reject(f"bundle_diameter {bundle_diameter} must be positive", param="bundle_diameter")

    length = 12.0
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    block_width = wall_thickness * 2 + channel_width
    block_height = base_thickness + channel_depth

    block = Box(block_width, length, block_height, align=(Align.MIN, Align.MIN, Align.MIN))
    channel = Box(channel_width, length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN))
    channel = Pos(wall_thickness, 0, base_thickness) * channel
    body = block - channel

    tab = Box(tab_length, length, base_thickness, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = Pos(block_width, 0, 0) * tab
    body = body + tab

    hole = Cylinder(
        hole_diameter / 2,
        base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    hole = Pos(block_width + tab_length / 2, length / 2, -1.0) * hole
    body = body - hole

    if draft:
        return body

    # The channel is fit-critical mating geometry and stays square: no chamfer on its
    # floor, its inner walls, or its mouth. `polish` only ever sees what is left over.
    channel_x = (wall_thickness, wall_thickness + channel_width)
    channel_z = (base_thickness, block_height)
    hole_center = (block_width + tab_length / 2, length / 2)
    hole_radius = hole_diameter / 2
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)

    def keeper(e):
        if e.geom_type != GeomType.LINE:
            return False
        bb = e.bounding_box()
        if bb.max.Z <= bed:
            return False
        if channel_x[0] <= bb.min.X and bb.max.X <= channel_x[1] and channel_z[0] <= bb.min.Z and bb.max.Z <= channel_z[1]:
            return False
        if e in concave:
            return False
        # Never touch the screw hole's rim (fit-critical, and a seam on the bore).
        if abs(bb.min.X - bb.max.X) < 1e-6 and abs(bb.min.Y - bb.max.Y) < 1e-6:
            dist = ((bb.min.X - hole_center[0]) ** 2 + (bb.min.Y - hole_center[1]) ** 2) ** 0.5
            if abs(dist - hole_radius) < 1e-3:
                return False
        # The short top edges at each Y end would meet the vertical corner and the long
        # top edge in a three-way convex corner, leaving a sub-1mm2 triangle behind. Leave
        # those ends square rather than shave the doctrine's own allowed sliver.
        if abs(bb.min.Y - bb.max.Y) < 1e-6 and (bb.min.Y < 1e-6 or abs(bb.min.Y - length) < 1e-6):
            if abs(bb.min.X - bb.max.X) > 1e-6:
                return False
        return True

    keep = body.edges().filter_by(keeper)
    return polish(body, keep, 1.0)
