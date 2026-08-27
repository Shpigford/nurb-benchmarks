from math import cos, radians, sin

from nurb import *

# The row's shared interface: every rest on the bench carries the pole axis
# exactly this far above the bed, whatever the pole diameter is.
AXIS_HEIGHT = 18.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), rest_length=22.0, draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is, measured across
    rest_length: how much of the pole this rest supports, along its length
    """
    if rest_length < 20.0:
        reject(
            "rest_length %.1f is under the 20mm a rest needs to steady the pole: raise it to 20 or more"
            % rest_length,
            param="rest_length",
        )

    # 0.25 of air all round the soft finish: enough that the pole never binds,
    # close enough that the seat still hugs it.
    seat_radius = pole_diameter / 2 + 0.25
    seat_floor = AXIS_HEIGHT - seat_radius
    if seat_floor < 2.5:
        reject(
            "pole_diameter %.1f leaves under 2.5mm of material below the seat at the fixed 18mm axis height: keep it under %.1f"
            % (pole_diameter, 2 * (AXIS_HEIGHT - 2.5 - 0.25)),
            param="pole_diameter",
        )
    if pole_diameter < 5.0:
        reject(
            "pole_diameter %.1f is thinner than a rest this shape can usefully cradle: keep it at 5 or more"
            % pole_diameter,
            param="pole_diameter",
        )

    # The seat wraps 75 degrees each side of bottom dead centre, so the arc
    # stays comfortably past 120 degrees after the rim chamfer takes its bite.
    rim_angle = radians(75.0)
    rim_half = seat_radius * sin(rim_angle)
    top = AXIS_HEIGHT - seat_radius * cos(rim_angle)
    half_width = rim_half + 3.0  # 3mm of wall outboard of the seat, all the way up

    # A plinth carries the cradle to the bed; a 45 degree flare picks up the
    # cradle's full width just below the seat floor, so the pole's weight lands
    # on material all the way down.
    plinth_half = min(max(7.0, pole_diameter / 2 - 2.0), half_width - 0.5)
    flare_start = seat_floor - 0.5
    flare_top = flare_start + (half_width - plinth_half)

    if 2 * plinth_half * rest_length < 200.0:
        reject(
            "the footprint drops under 200mm2 of bed contact: raise rest_length",
            param="rest_length",
        )

    profile = Polygon(
        (plinth_half, 0.0),
        (plinth_half, flare_start),
        (half_width, flare_top),
        (half_width, top),
        (-half_width, top),
        (-half_width, flare_top),
        (-plinth_half, flare_start),
        (-plinth_half, 0.0),
        align=None,
    )
    body = extrude(Plane.XZ * profile, rest_length / 2, both=True)
    seat = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(seat_radius, rest_length + 10)
    body -= seat

    if draft:
        return body

    # Polish everything except edges lying in the bed face and the concave
    # junction where the flare meets the plinth.
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > 0.01
        and not any(e.is_same(c) for c in concave)
    )
    return polish(body, keep, 1.2)
