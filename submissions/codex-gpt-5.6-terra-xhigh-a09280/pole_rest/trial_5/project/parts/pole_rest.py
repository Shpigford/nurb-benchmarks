from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), length=25.0):
    """A support-free drying saddle for a finished pole.

    pole_diameter: measured diameter of the pole held in the saddle.
    length: length of the saddle along the pole's direction of travel (Y).
    """
    axis_height = 18.0
    radial_clearance = 0.25
    backing_thickness = 2.5

    if pole_diameter <= 0.0:
        reject("pole_diameter must be positive", param="pole_diameter")

    seat_radius = pole_diameter / 2.0 + radial_clearance
    if seat_radius >= axis_height - 1.2:
        reject(
            "pole_diameter is too large to leave 1.2mm of material below the seat at the fixed 18mm axis height",
            param="pole_diameter",
        )
    if length < 20.0:
        reject("length must be at least 20mm so the pole is supported along its length", param="length")

    # The saddle is deliberately open above the pole centre. Its top intersects the
    # lower circular seat at +/-63.3 degrees from bottom, giving a 126.6 degree
    # continuous cradle while leaving an unobstructed vertical drop-in path.
    body_height = axis_height - 0.45 * seat_radius
    body_width = 2.0 * (seat_radius + backing_thickness)
    body = Box(body_width, length, body_height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # A horizontal cylinder makes a constant-radius seat along all of Y. It extends
    # past both ends so no end cap can touch the pole.
    seat = Cylinder(
        seat_radius,
        length + 2.0,
        rotation=(90.0, 0.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).translate((0.0, 0.0, axis_height))
    return body - seat
