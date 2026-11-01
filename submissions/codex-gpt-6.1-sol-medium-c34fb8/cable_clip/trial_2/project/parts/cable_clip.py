from nurb import *


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter"))):
    """Screw-down clip with a square, open cable channel along Y.

    bundle_diameter: measured width of the cable bundle held in the channel.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    length = 12.0
    tab_length = 10.0
    outside_width = channel_width + 2.0 * wall_thickness

    # The base includes the tab, so its bottom is one uninterrupted bed face.
    body = Pos(tab_length / 2.0, 0, 0) * Box(
        outside_width + tab_length, length, base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    wall_center = (channel_width + wall_thickness) / 2.0
    for x in (-wall_center, wall_center):
        body += Pos(x, 0, base_thickness) * Box(
            wall_thickness, length, bundle_diameter,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Center the screw in the tab's 10 x 12 mm rectangle.
    screw_x = outside_width / 2.0 + tab_length / 2.0
    body -= Pos(screw_x, 0, -1.0) * Cylinder(
        4.2 / 2.0, base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body
