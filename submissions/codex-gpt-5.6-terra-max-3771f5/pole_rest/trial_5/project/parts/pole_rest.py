from nurb import *


# This is intentionally read from measurements.toml, while remaining a normal float
# default in the part signature so the viewer and callers can size it for a nearby pole.
MEASURED_POLE_DIAMETER = measured("pole_diameter")


@part
def pole_rest(
    pole_diameter=MEASURED_POLE_DIAMETER,
    rest_length=22.0,
    side_wall=4.0,
    clearance=0.25,
):
    """A support-free, drop-in drying cradle for a finished pole.

    pole_diameter: measured diameter of the pole being supported
    rest_length: length of the cradle in the pole's direction
    side_wall: radial material behind each side of the pole seat
    clearance: radial clearance between the finished pole and its cradle
    """
    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than 0 mm", param="pole_diameter")
    if rest_length < 20.0:
        reject("rest_length must be at least 20 mm", param="rest_length")
    if side_wall < 1.2:
        reject("side_wall must be at least 1.2 mm", param="side_wall")
    if clearance < 0.1:
        reject("clearance must be at least 0.1 mm", param="clearance")

    # The pole's centerline is fixed by the brief, independent of its diameter.
    axis_height = 18.0
    seat_radius = pole_diameter / 2.0 + clearance
    half_width = seat_radius + side_wall

    # A block cut by a horizontal cylinder makes a true lower semicircular cradle.
    # Keeping the block top at the centerline leaves the upper half open for a
    # straight-down drop-in, while the full lower 180 degrees is backed by material.
    body = Box(
        2.0 * half_width,
        rest_length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat_cutter = Cylinder(
        seat_radius,
        rest_length + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).rotate(Axis.X, 90.0).translate((0.0, 0.0, axis_height))
    return body - seat_cutter
