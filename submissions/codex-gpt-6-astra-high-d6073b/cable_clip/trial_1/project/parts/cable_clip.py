from nurb import *


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter"))):
    """Screw-down clip with a square, open channel along Y.

    bundle_diameter: measured cable bundle width; sets channel width and depth.
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be greater than zero", param="bundle_diameter")

    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    length = 12.0
    tab_length = 10.0
    outside_width = channel_width + 2 * wall_thickness

    # One continuous bottom plate includes the mounting tab on the +X side.
    body = Pos(tab_length / 2, 0, 0) * Box(
        outside_width + tab_length, length, base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for side in (-1, 1):
        body += Pos(side * (channel_width + wall_thickness) / 2, 0, base_thickness) * Box(
            wall_thickness, length, bundle_diameter,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    hole_x = outside_width / 2 + tab_length / 2
    body -= Pos(hole_x, 0, -1) * Cylinder(
        4.2 / 2, base_thickness + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # The specified square channel and constant wall/tab thicknesses are intentional.
    return body
