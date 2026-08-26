from nurb import *
from math import cos, radians, sqrt

POLE_AXIS_HEIGHT = 18.0  # fixed by the row of rests on the bench: pole axis above the bed


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    length=24.0,
    wall_thickness=2.5,
    cradle_wrap_angle=75.0,
    pole_clearance=0.1,
    draft=False,
):
    """A cradle that holds a freshly finished pole while it dries.

    pole_diameter: how thick the pole is; the seat is cut to match it
    length: how long the rest is along the pole
    wall_thickness: how much material backs the seat at its rim
    cradle_wrap_angle: how far up each side of the pole the seat wraps, in degrees from the bottom
    pole_clearance: gap left between the seat and the pole so the finish never touches on the way in
    """
    r = pole_diameter / 2.0 + pole_clearance
    if r + wall_thickness >= POLE_AXIS_HEIGHT:
        reject(
            f"pole_diameter {pole_diameter} leaves no base under the seat: keep the "
            f"radius under {POLE_AXIS_HEIGHT - wall_thickness - pole_clearance:.1f}",
            param="pole_diameter",
        )
    if not 0 < cradle_wrap_angle < 90:
        reject("cradle_wrap_angle must stay under 90 so the pole drops straight in", param="cradle_wrap_angle")
    if length < 20.0:
        reject("length under 20 is too short to steady the pole", param="length")

    a = radians(cradle_wrap_angle)
    top = POLE_AXIS_HEIGHT - r * cos(a)          # rim height where the seat stops wrapping
    half_width = r + wall_thickness              # rim wall backed by wall_thickness at its widest

    body = Box(2 * half_width, length, top, align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Cylinder(r, length + 2, rotation=(90, 0, 0)).moved(Location((0, 0, POLE_AXIS_HEIGHT)))
    body = body - seat
    if draft:
        return body
    bed = body.bounding_box().min.Z
    concave = set(concave_edges(body))
    def on_seat(e):
        # Edges bordering the seat stay sharp: the seat is fit geometry, and chamfering
        # its rim leaves sliver faces where three chamfers meet at each corner.
        return any(
            abs(sqrt(v.X ** 2 + (v.Z - POLE_AXIS_HEIGHT) ** 2) - r) < 0.05 for v in e.vertices()
        )

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and e not in concave and not on_seat(e)
    )
    return polish(body, keep, 1.0)
