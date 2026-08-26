from nurb import *


@part
def pole_rest(pole_diameter=None, length=22.0, seat_gap=0.25, draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how wide the pole is across
    length: how long the rest runs under the pole
    seat_gap: how much air sits between the seat and the pole's finish
    """
    if pole_diameter is None:
        pole_diameter = measured("pole_diameter")
    axis_height = 18.0  # the pole's axis over the bed; fixed by the row of rests
    pole_r = pole_diameter / 2
    seat_r = pole_r + seat_gap

    # Seat clearance must stay between the fit floor and the contact ceiling.
    if seat_gap < 0.1 or seat_gap > 0.35:
        reject(
            "seat_gap %.2f leaves the seat either touching the finish or too far"
            " to support it: keep it between 0.1 and 0.35" % seat_gap,
            param="seat_gap",
        )
    # The seat floor needs solid material under it, and the lip must stay below
    # the pole's axis so the pole drops straight in.
    if axis_height - seat_r < 2.0:
        reject(
            "pole_diameter %.1f puts the seat floor under 2mm off the bed at the"
            " fixed 18mm axis height: this rest tops out near 31mm poles"
            % pole_diameter,
            param="pole_diameter",
        )

    lip_drop = 0.3 * pole_r  # lip this far below the axis gives ~145 deg of cradle
    top = axis_height - lip_drop
    half_width = seat_r + 1.75  # 1.2 of backing behind the lip, plus chamfer room

    body = Pos(0, 0, top / 2) * Box(2 * half_width, length, top)
    seat = Pos(0, 0, axis_height) * Rot(90, 0, 0) * Cylinder(seat_r, length + 2)
    body = body - seat

    if draft:
        return body
    keep = body.edges().filter_by(lambda e: e.bounding_box().max.Z > 1e-6)
    keep = [e for e in keep if e not in concave_edges(body)]
    return polish(body, keep, 1.0)
