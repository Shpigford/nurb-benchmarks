from nurb import *

# The pole's axis sits at this height above the bed no matter the pole size;
# the rig it lies across is fixed, only the cradle around it changes.
AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    rest_length=24.0,
    cradle_clearance=0.25,
    cradle_wall=2.5,
    draft=False,
):
    """
    pole_diameter: how thick the pole being dried is, across
    rest_length: how far the cradle runs along the pole
    cradle_clearance: gap left between the cradle and the pole's surface
    cradle_wall: how much material backs the cradle behind the pole
    """
    if pole_diameter <= 0:
        reject(f"pole_diameter {pole_diameter} must be positive", param="pole_diameter")
    if cradle_clearance < 0.1:
        reject(
            f"cradle_clearance {cradle_clearance} is under the 0.1mm the pole "
            "needs to drop in and lift free: raise it above 0.1",
            param="cradle_clearance",
        )
    if rest_length < 20.0:
        reject(
            f"rest_length {rest_length} is under the 20mm a rest needs along the pole: "
            "raise it above 20.0",
            param="rest_length",
        )

    seat_radius = pole_diameter / 2.0 + cradle_clearance
    below = AXIS_HEIGHT - seat_radius
    if below < cradle_wall:
        reject(
            f"pole_diameter {pole_diameter} leaves only {below:.2f}mm of material "
            f"under the seat, under the {cradle_wall}mm cradle_wall needs: lower "
            "pole_diameter or cradle_wall",
            param="pole_diameter",
        )

    half_width = seat_radius + cradle_wall
    width = 2 * half_width

    block = Box(
        width,
        rest_length,
        AXIS_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # A semicircular groove, open on top, concentric with the pole's final
    # position: nothing sits above axis height, so the pole drops straight
    # down the whole way in and never has to clear an overhang to seat.
    groove = Pos(0, 0, AXIS_HEIGHT) * Cylinder(
        seat_radius, rest_length + 4.0, rotation=(90, 0, 0)
    )

    body = block - groove
    if draft:
        return body

    bed = body.bounding_box().min.Z
    seat_faces = body.faces().filter_by(GeomType.CYLINDER)
    seat_edges = seat_faces.edges()
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e not in seat_edges
        and e not in concave
    )
    return polish(body, keep, 1.0)
