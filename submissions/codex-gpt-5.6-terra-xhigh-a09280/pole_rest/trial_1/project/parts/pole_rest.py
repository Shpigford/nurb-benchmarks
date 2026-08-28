from nurb import *


@part
def pole_rest(pole_diameter: float = 20.0, draft: bool = False):
    """A low, open-top drying rest for a finished pole.

    pole_diameter: measured diameter of the pole held by the cradle.
    """
    # The pole's centre is intentionally fixed at z=18 mm. The small radial
    # clearance protects a soft finish while keeping the broad lower cradle
    # close enough to support it.
    axis_height = 18.0
    radial_clearance = 0.25
    cradle_radius = pole_diameter / 2.0 + radial_clearance
    length = 23.0
    width = 24.0

    base = Box(
        width,
        length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    groove = (
        Cylinder(cradle_radius, length + 2.0)
        .rotate(Axis.X, 90)
        .translate((0, length / 2.0 + 1.0, axis_height))
    )
    return base.cut(groove)
