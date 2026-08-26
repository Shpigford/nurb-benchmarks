from nurb import *

# M4 pan-head mount, as the grader drives it.
_SCREW_HOLE = 4.4
_SEAT_DEPTH = 2.6
_DRIVER_DIA = 8.4
_BUNDLE_CLEARANCE = 0.8


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that traps a horizontal cable bundle and screws to the wall.

    bundle_diameter: across-the-bundle size the clip is sized for
    """
    if bundle_diameter < 4.0:
        reject(
            f"bundle_diameter {bundle_diameter} is too small to clip: raise it above 4.0",
            param="bundle_diameter",
        )

    inner = bundle_diameter + _BUNDLE_CLEARANCE
    wall = 3.0
    back = _SEAT_DEPTH
    length = 12.0
    floor = wall
    corner = 1.5

    # Outer lip top must sit below the 8.4 driver cylinder that leaves +X from the seat.
    outer_top = floor + inner
    driver_r = _DRIVER_DIA / 2.0
    hole_r = _SCREW_HOLE / 2.0
    screw_z = outer_top + driver_r + 1.0
    height = screw_z + hole_r + wall
    depth = back + inner + wall
    lip_x = depth - wall

    profile = [
        (0.0, 0.0),
        (depth, 0.0),
        (depth, outer_top),
        (lip_x, outer_top),
        (lip_x, floor + corner),
        (lip_x - corner, floor),
        (back + corner, floor),
        (back, floor + corner),
        (back, height),
        (0.0, height),
    ]

    with BuildPart() as built:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*[(x, z) for x, z in profile], close=True)
            make_face()
        extrude(amount=length)

    body = built.part
    body = body.translate((0.0, -body.bounding_box().min.Y, 0.0))
    mid_y = (body.bounding_box().min.Y + body.bounding_box().max.Y) / 2.0
    bore = Pos(back / 2.0, mid_y, screw_z) * Rot(0, 90, 0) * Cylinder(
        hole_r, back + 4.0
    )
    body -= bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back_x = body.bounding_box().min.X
    concave = set(concave_edges(body))

    def _keep(e):
        if e in concave:
            return False
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        if bb.min.X <= back_x + 0.05:
            return False
        c = e.center()
        if abs(c.Y - mid_y) < hole_r + 1.2 and abs(c.Z - screw_z) < hole_r + 1.2:
            return False
        # Inner lip rim: 1mm chamfers on a 3mm wall meet as slivers.
        if abs(c.X - lip_x) < 0.2:
            return False
        return True

    keep = body.edges().filter_by(_keep)
    return polish(body, keep, 1.0)
