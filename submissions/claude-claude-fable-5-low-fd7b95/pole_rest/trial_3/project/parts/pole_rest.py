from math import cos, radians, sin

from nurb import *

# The pole lies along Y with its axis exactly this far above the bed; the row of
# rests shares this interface, so it is a constant, not a parameter.
AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    length=22.0,
    seat_clearance=0.2,
    lip_wall=2.2,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how wide the pole is, measured across
    length: how long the rest runs along the pole
    seat_clearance: extra room in the seat so the seat never touches the wet finish hard
    lip_wall: how much material backs the top lip of the seat
    """
    seat_radius = pole_diameter / 2.0 + seat_clearance
    half_arc = radians(65.0)  # 130 degree cradle, margin over the 120 the pole needs
    top = AXIS_HEIGHT - seat_radius * cos(half_arc)
    if top <= 4.0:
        reject(
            f"pole_diameter {pole_diameter} leaves the seat floor under 4mm of "
            "material at an 18mm axis height: use a smaller pole",
            param="pole_diameter",
        )
    half_width = seat_radius * sin(half_arc) + lip_wall

    body = Box(
        2.0 * half_width,
        length,
        top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(seat_radius, length + 2.0)
    body = body - seat

    if draft:
        return body

    # Chamfer exposed edges, but never the seat: a chamfer on the lip eats into
    # the cradle arc, and the bottom face stays flat on the bed.
    def exposed(e):
        if e.bounding_box().max.Z <= 1e-6:
            return False
        for v in e.vertices():
            if (v.X**2 + (v.Z - AXIS_HEIGHT) ** 2) ** 0.5 < seat_radius + 0.8:
                return False
        return True

    keep = body.edges().filter_by(exposed)
    return polish(body, keep, 1.0)
