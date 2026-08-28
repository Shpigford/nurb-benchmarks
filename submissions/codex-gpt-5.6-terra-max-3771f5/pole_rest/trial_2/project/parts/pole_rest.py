from math import cos, radians

from nurb import *


@part
def pole_rest(
    pole_diameter: float = measured("pole_diameter"),
    rest_length: float = 26.0,
    draft: bool = False,
):
    """A print-in-place drying rest with a continuous cylindrical saddle.

    pole_diameter: outside diameter of the finished pole that the saddle cradles
    rest_length: length of the saddle along the pole
    """
    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")
    if rest_length < 20.0:
        reject("rest_length must be at least 20.0 mm", param="rest_length")

    axis_height = 18.0
    clearance = 0.2
    backing = 2.4

    # A 134 degree lower arc is open above the pole, so the pole can be dropped
    # vertically into place while still being supported over more than 120 degrees.
    cradle_radius = pole_diameter / 2.0 + clearance
    saddle_half_angle = 67.0
    base_height = axis_height - cradle_radius * cos(radians(saddle_half_angle))
    base_width = 2.0 * (cradle_radius + backing)

    # Primitives are centered by default; move the footprint so the printed bed is Z=0.
    base = Box(base_width, rest_length, base_height).translate((0.0, 0.0, base_height / 2.0))
    bore = Cylinder(
        cradle_radius,
        rest_length + 2.0,
        rotation=(90.0, 0.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).translate((0.0, 0.0, axis_height))

    # The oversize bore is a clearance-controlled, fit-critical surface; do not
    # polish it. The rectangular footprint keeps the base broad and fully grounded.
    return base - bore
