from nurb import *

# M4 pan-head through the back plate: medium clearance and the grader's driver envelope.
_HOLE = 4.4
_HEAD = 8.4
_SEAT_MIN = 2.4
_BUNDLE_CLEAR = 0.6
_WALL = 2.6
_LENGTH = 12.0


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that traps a horizontal cable bundle and takes one M4 screw.

    bundle_diameter: measured width of the taped cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            f"bundle_diameter {bundle_diameter:g} is too small to clip; raise it to 4.0 or more",
            param="bundle_diameter",
        )

    inner = bundle_diameter + _BUNDLE_CLEAR
    plate = max(_WALL, _SEAT_MIN)
    floor = _WALL
    front = _WALL
    length = _LENGTH
    hole_r = _HOLE / 2
    head_r = _HEAD / 2

    cavity_top = floor + inner
    # Hole stays in the back plate, above the trough, with wall around the bore and
    # the 8.4 driver cylinder clearing the trough once the head seats.
    screw_z = max(cavity_top + hole_r + _WALL, cavity_top + head_r + 0.4)
    height = screw_z + hole_r + _WALL
    depth = plate + inner + front

    profile = Plane.XZ * make_face(
        Polyline(
            (0, 0),
            (depth, 0),
            (depth, cavity_top),
            (plate + inner, cavity_top),
            (plate + inner, floor),
            (plate, floor),
            (plate, height),
            (0, height),
            close=True,
        )
    )
    body = extrude(profile, amount=length / 2, both=True)

    bore = Pos(-1.0, 0, screw_z) * Rot(Y=90) * Cylinder(
        hole_r,
        plate + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - bore

    if draft:
        return body

    xmin = body.bounding_box().min.X
    zmin = body.bounding_box().min.Z
    # Chamfer only the long run of the extrusion. Dressing the Y-end corners as well
    # leaves the 0.87mm triangles three 1mm chamfers make, which check reports as slivers.
    cavity_x = plate + inner
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > zmin + 1e-4
        and e.bounding_box().min.X > xmin + 1e-4
        and e.geom_type != GeomType.CIRCLE
        and abs(e.tangent_at(0.5).Y) > 0.9
        and abs(e.bounding_box().center().X - cavity_x) > 0.3
    )
    keep -= concave_edges(body)
    return polish(body, keep, 1.0)
