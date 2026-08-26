from nurb import *

AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    rest_length=22.0,
    seat_clearance=0.2,
    side_wall=3.0,
    floor_thickness=4.0,
    chamfer_size=1.0,
    draft=False,
):
    """A cradle that holds a freshly finished pole while it dries.

    pole_diameter: how thick the pole is across
    rest_length: how far the rest runs along the pole
    seat_clearance: gap between the seat and the finished surface
    side_wall: material outside the seat on each side
    floor_thickness: material under the bottom of the seat
    chamfer_size: size of the chamfer on the exposed edges
    """
    seat_radius = pole_diameter / 2.0 + seat_clearance

    if AXIS_HEIGHT - seat_radius < floor_thickness:
        reject(
            f"pole_diameter {pole_diameter} leaves only "
            f"{AXIS_HEIGHT - seat_radius:.1f}mm under the seat at the fixed "
            f"{AXIS_HEIGHT}mm axis height: keep it under "
            f"{2 * (AXIS_HEIGHT - floor_thickness - seat_clearance):.1f}",
            param="pole_diameter",
        )

    width = 2.0 * (seat_radius + side_wall)

    body = Pos(0, 0, AXIS_HEIGHT / 2.0) * Box(width, rest_length, AXIS_HEIGHT)

    # The seat is a half-round the pole's own size, open straight up: its widest
    # point is the axis height, so the pole drops in vertically.
    seat = Rot(90, 0, 0) * Cylinder(seat_radius, rest_length + 2.0)
    seat = Pos(0, 0, AXIS_HEIGHT) * seat

    rest = body - seat

    if draft:
        return rest

    bed = rest.bounding_box().min.Z
    concave = concave_edges(rest)
    seat_face = rest.faces().filter_by(GeomType.CYLINDER)
    seat_rim = [e for f in seat_face for e in f.edges()]
    keep = [
        e
        for e in rest.edges()
        if e.bounding_box().min.Z > bed + 1e-6
        and not any(e.is_same(c) for c in concave)
        and not any(e.is_same(r) for r in seat_rim)
    ]
    return polish(rest, keep, chamfer_size)
