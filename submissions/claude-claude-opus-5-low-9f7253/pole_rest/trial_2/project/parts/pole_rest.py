from nurb import *

POLE_DIAMETER = measured("pole_diameter")  # calipers across the sanded pole
AXIS_HEIGHT = 18.0  # the pole's axis sits exactly this far above the bench, fixed by the row of rests


@part
def pole_rest(
    pole_diameter=POLE_DIAMETER,
    rest_length=24.0,
    wall_thickness=2.5,
    pole_clearance=0.25,
    chamfer_size=1.0,
    draft=False,
):
    """A cradle that holds a freshly finished pole off the bench while it dries.

    pole_diameter: how thick the pole is across
    rest_length: how far the rest runs along the pole
    wall_thickness: how much material sits behind the cradle surface
    pole_clearance: the gap between the cradle and the wet finish
    chamfer_size: how big the chamfers on the exposed edges are
    """
    radius = pole_diameter / 2.0
    seat_radius = radius + pole_clearance

    if seat_radius + wall_thickness > AXIS_HEIGHT:
        reject(
            f"pole_diameter {pole_diameter} needs {2 * (seat_radius + wall_thickness):.1f}mm of"
            f" height but the pole axis is fixed at {AXIS_HEIGHT}mm: use a pole under"
            f" {2 * (AXIS_HEIGHT - wall_thickness - pole_clearance):.1f}mm across",
            param="pole_diameter",
        )

    width = 2.0 * (seat_radius + wall_thickness)

    body = Pos(0, 0, AXIS_HEIGHT / 2.0) * Box(width, rest_length, AXIS_HEIGHT)
    seat = (
        Pos(0, 0, AXIS_HEIGHT)
        * Rot(90, 0, 0)
        * Cylinder(radius=seat_radius, height=rest_length + 2.0)
    )
    shape = body - seat

    if draft:
        return shape

    bed = shape.bounding_box().min.Z
    concave = set(concave_edges(shape))
    # The seat is the mating surface; its rim gets no lead-in chamfer.
    seat_faces = shape.faces().filter_by(GeomType.CYLINDER)
    seat_edges = set(e for f in seat_faces for e in f.edges())
    keep = shape.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e not in concave
        and e not in seat_edges
    )
    return polish(shape, keep, chamfer_size)
