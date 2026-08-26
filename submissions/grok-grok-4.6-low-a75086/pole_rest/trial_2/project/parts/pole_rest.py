from nurb import *

AXIS_HEIGHT = 18.0
# Gap to the finish: enough not to touch, close enough to cradle.
SEAT_CLEARANCE = 0.2


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    rest_length=22.0,
    wall_thickness=2.4,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: width of the pole across
    rest_length: how far the rest runs along the pole
    wall_thickness: material behind the cradle surface
    """
    if pole_diameter < 8.0:
        reject(
            "pole_diameter is too small for a printable cradle; raise it to at least 8",
            param="pole_diameter",
        )
    if rest_length < 20.0:
        reject(
            "rest_length must be at least 20 so the pole sits on a real seat",
            param="rest_length",
        )
    if wall_thickness < 1.4:
        reject(
            "wall_thickness must stay at least 1.4 so the cradle has backing",
            param="wall_thickness",
        )

    pole_radius = pole_diameter / 2.0
    seat_radius = pole_radius + SEAT_CLEARANCE
    # Seat floor is AXIS_HEIGHT - seat_radius; leave a printable slab under it.
    if AXIS_HEIGHT - seat_radius < 2.0:
        reject(
            "pole_diameter is too large to cradle at 18mm axis height; lower it",
            param="pole_diameter",
        )

    width = 2.0 * (seat_radius + wall_thickness)
    height = AXIS_HEIGHT

    body = Box(width, rest_length, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Cylinder(
        seat_radius,
        rest_length + 4.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    seat = seat.rotate(Axis.X, 90).move(Location((0, 0, AXIS_HEIGHT)))
    # Open the top so the pole drops straight down into the seat.
    opening = Box(
        2.0 * seat_radius,
        rest_length + 4.0,
        pole_diameter + 8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).move(Location((0, 0, AXIS_HEIGHT)))
    body = body - seat - opening

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        c = bb.center()
        dist_from_axis = ((c.X) ** 2 + (c.Z - AXIS_HEIGHT) ** 2) ** 0.5
        # Leave the seat and its rims sharp so polish does not leave slivers.
        return dist_from_axis > seat_radius + 0.8

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
