from nurb import *


@part
def pole_rest(pole_diameter=20.0, draft=False):
    """A support-free, drop-in cradle for a freshly finished pole.

    pole_diameter: diameter of the pole being dried
    """
    if pole_diameter <= 2.0:
        return reject("pole_diameter must be greater than 2.0mm for a printable cradle", param="pole_diameter")

    # The measured 20mm pole gets 0.2mm radial air.  The groove is cut from a
    # grounded block, so its cylindrical wall is continuous along Y and has
    # solid material behind it instead of only a knife-edge contact.
    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + 0.2
    footprint = max(24.0, pole_diameter + 4.0)
    base_height = 15.0

    base = Box(
        footprint,
        footprint,
        base_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    groove = Pos(0, 0, 18.0) * Cylinder(
        cradle_radius,
        footprint + 4.0,
        rotation=(90, 0, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    body = base - groove

    if draft:
        return body

    # Keep the bed face flat.  The remaining exposed edges receive the standard
    # 1mm finish chamfer; the groove itself remains a smooth fit surface.
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    return polish(body, keep, 1.0)
