from nurb import *


@part
def pole_rest(pole_diameter=20.0, length=24.0, base_width=26.0, clearance=0.2, draft=False):
    """A cradle that holds a drying pole with its axis 18mm above the bed.

    pole_diameter: how thick the pole is
    length: how long the rest is along the pole
    base_width: how wide the block is across the pole
    clearance: gap between the pole and the cradle surface
    """
    axis_z = 18.0
    r = pole_diameter / 2.0
    seat_r = r + clearance
    # top sits below the axis so the pole can drop straight in; a 145 degree cradle at 20mm
    top = axis_z - r * 0.3
    width = max(base_width, 2 * (seat_r + 1.2) + 4)
    body = Box(width, length, top, align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Cylinder(seat_r, length + 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    seat = seat.rotate(Axis.X, 90).translate((0, 0, axis_z))
    body = body - seat
    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    return polish(body, keep, 1.0)
