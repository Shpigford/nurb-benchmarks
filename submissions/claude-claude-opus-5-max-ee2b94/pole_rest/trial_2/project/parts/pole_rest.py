from math import cos, radians, sin

from nurb import *


@part
def pole_rest(
    pole_diameter=20.0,
    pole_height=18.0,
    cradle_gap=0.25,
    cradle_wrap=140.0,
    wall_thickness=3.0,
    rest_length=22.0,
    draft=False,
):
    """A saddle that holds a freshly finished pole clear of the bench while it dries.

    pole_diameter: how thick the pole is, measured across
    pole_height: how high the pole's centre sits above the bench, shared by every rest in the row
    cradle_gap: how much wider than the pole the cradle is cut, so the wet finish is never pinched
    cradle_wrap: how far around the pole the cradle reaches, in degrees
    wall_thickness: how much material stands behind the cradle at its rim
    rest_length: how much of the pole's length this one rest bears on
    """
    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + cradle_gap
    cradle_bottom = pole_height - cradle_radius

    if cradle_wrap < 120.0:
        reject("under 120 degrees of wrap the pole balances on two edges instead of being cradled", "cradle_wrap")
    if cradle_wrap > 175.0:
        reject("past 175 degrees the cradle closes over the pole and it can no longer be dropped in", "cradle_wrap")
    if cradle_bottom < 3.0:
        reject("this pole is too fat to sit that low: the cradle would cut through the bench floor", "pole_diameter")

    half = radians(cradle_wrap / 2.0)
    rim_x = cradle_radius * sin(half)
    # The rim stops at the wrap angle, so the saddle's own top never reaches the pole's
    # centre height and nothing leans over the drop-in path.
    top_z = pole_height - cradle_radius * cos(half)
    half_width = rim_x + wall_thickness

    body = Pos(0, 0, top_z / 2) * Box(2 * half_width, rest_length, top_z)
    body -= Pos(0, 0, pole_height) * Rot(90, 0, 0) * Cylinder(cradle_radius, rest_length + 4)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    seat = body.faces().filter_by(GeomType.CYLINDER)
    seat_edges = [e for f in seat for e in f.edges()]
    # The short cross-edges at the top stay sharp on purpose: chamfering them too would
    # meet the other two chamfers at each corner and leave four sliver triangles.
    cross = body.edges().filter_by(Axis.X)
    keep = [
        e
        for e in body.edges()
        if e.bounding_box().max.Z > bed + 1e-6  # nothing lying in the bed face
        and not any(e.is_same(c) for c in concave)
        and not any(e.is_same(s) for s in seat_edges)  # the seat is fit geometry
        and not any(e.is_same(x) for x in cross)
    ]
    return polish(body, keep, 1.0)
