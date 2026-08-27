from math import cos, hypot, radians, sin

from nurb import *

AXIS_HEIGHT = 18.0  # the bench interface: every rest in the row holds the pole axis exactly here
WRAP_DEG = 72.0     # the cradle reaches this far each side of bottom dead centre, 144 degrees in all
SIDE_PAD = 3.4      # material outboard of the seat rim, sized so the polish still leaves over 2mm of wall
CHAMFER = 1.2       # one size everywhere; at 1.2 the corner triangles land over the 1mm2 sliver line


@part
def pole_rest(pole_diameter=measured("pole_diameter"), length=22.0,
              pole_clearance=0.2, draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is
    length: how much of the pole each rest supports along its run
    pole_clearance: breathing room around the pole so it drops in without scraping the finish
    """
    if pole_clearance < 0.12:
        reject(f"pole_clearance {pole_clearance} will bind on the pole once printed: "
               "keep it at 0.15 or more", param="pole_clearance")
    if pole_clearance > 0.3:
        reject(f"pole_clearance {pole_clearance} leaves the pole clear of the cradle "
               "instead of resting in it: keep it at 0.3 or less", param="pole_clearance")
    if pole_diameter < 3.0:
        reject(f"pole_diameter {pole_diameter} is thinner than the cradle can usefully hold: "
               "3mm is the floor", param="pole_diameter")
    if pole_diameter > 31.0:
        reject(f"pole_diameter {pole_diameter} leaves under 2mm of material below the seat "
               "with the axis fixed at 18mm: 31 is the ceiling for this bench line",
               param="pole_diameter")
    if length < 8.0:
        reject(f"length {length} is too short to steady a pole or carry its chamfers: "
               "keep it at 8 or more", param="length")

    seat_radius = pole_diameter / 2 + pole_clearance
    top = AXIS_HEIGHT - seat_radius * cos(radians(WRAP_DEG))
    half_width = seat_radius * sin(radians(WRAP_DEG)) + SIDE_PAD

    body = Box(2 * half_width, length, top,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(seat_radius, length + 2)
    body = body - seat

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def on_seat(e):
        p = e @ 0.5
        return abs(hypot(p.X, p.Z - AXIS_HEIGHT) - seat_radius) < 0.05

    # The seat is the mating surface, so its rim stays sharp: no lead-in chamfer,
    # and the full 144 degree arc reaches the top face untouched.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > bed + 1e-4 and not on_seat(e))
    return polish(body, keep, CHAMFER)
