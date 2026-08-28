from math import cos, radians, sin

from nurb import *

# The row of rests on the bench fixes the interface: the pole lies along Y with its
# axis exactly this far above the bed, centred over the footprint. Not a parameter.
AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_clearance=0.3,
    cradle_wall=3.0,
    cradle_wrap=140.0,
    rest_length=24.0,
    chamfer_size=1.0,
    draft=False,
):
    """One of a row of bench rests that cradle a freshly finished pole while it dries.

    pole_diameter: how thick the pole is across
    pole_clearance: gap between the wet pole and the cradle, so the finish never touches
    cradle_wall: material behind the cradle where it is thinnest, up at the rim
    cradle_wrap: how far around the pole the cradle reaches, in degrees
    rest_length: how much of the pole's length this one rest holds
    chamfer_size: the facet on every exposed edge
    """
    seat_radius = pole_diameter / 2.0 + pole_clearance
    floor = AXIS_HEIGHT - seat_radius
    if floor < 3.0:
        reject(
            f"a {pole_diameter:.1f}mm pole seated {AXIS_HEIGHT:.0f}mm up leaves only "
            f"{floor:.1f}mm of floor under the cradle: keep pole_diameter under "
            f"{2 * (AXIS_HEIGHT - 3.0 - pole_clearance):.1f}",
            param="pole_diameter",
        )
    if not 120.0 <= cradle_wrap <= 175.0:
        reject(
            "cradle_wrap holds the pole between 120 and 175 degrees: under 120 the pole "
            "balances on two lines instead of lying in a cradle, over 175 the seat closes "
            "over it and it will not drop in",
            param="cradle_wrap",
        )

    half_wrap = radians(cradle_wrap / 2.0)
    # The rim is where the cradle stops. Everything outward of the seat sits at a radius
    # larger than the pole's, so the pole lowers straight down into it without touching.
    rim_z = AXIS_HEIGHT - seat_radius * cos(half_wrap)
    rim_x = seat_radius * sin(half_wrap)
    # Width is set at the rim, the one place the wall behind the seat runs thinnest.
    half_width = (seat_radius + cradle_wall) * sin(half_wrap)

    body = Pos(Z=rim_z / 2) * Box(2 * half_width, rest_length, rim_z)
    body -= Pos(Z=AXIS_HEIGHT) * Rot(X=90) * Cylinder(seat_radius, rest_length + 4)

    if draft:
        return body

    # The seat is mating geometry: its rim and its end arcs stay sharp, so the cradle
    # keeps every degree of its wrap. Everything outward of the rim, and off the bed,
    # takes the facet.
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: _outer(e, bed, rim_x, rim_z))
    return polish(body, keep, chamfer_size)


def _outer(edge, bed, rim_x, rim_z):
    """True for an exposed edge the polish pass may take."""
    box = edge.bounding_box()
    if box.max.Z <= bed + 1e-6:
        return False  # lies in the bed-contact face
    if max(abs(box.min.X), abs(box.max.X)) <= rim_x + 1e-6:
        return False  # the seat's rim and its end arcs, which stay sharp
    # The stub across each end of the rim is the third facet arriving at a corner the
    # flank and rim facets already share, and three chamfers at one corner leave the
    # sliver triangle the sliver rule counts.
    return not (box.min.Z >= rim_z - 1e-6 and box.max.X - box.min.X > 1e-6)
