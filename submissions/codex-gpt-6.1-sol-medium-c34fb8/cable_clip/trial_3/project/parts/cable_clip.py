from nurb import *


@part
def cable_clip(bundle_diameter=8.0):
    """Screw-down clip with a square, open channel along Y.

    bundle_diameter: measured width of the cable bundle; sets channel width and depth.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than zero", param="bundle_diameter")

    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    length = 12.0
    tab_length = 10.0
    clip_width = channel_width + 2.0 * wall_thickness

    # Origin at the lower left corner of the clip; the tab extends to +X.
    body = Box(clip_width + tab_length, length, base_thickness,
               align=(Align.MIN, Align.MIN, Align.MIN))
    body += Pos(0, 0, base_thickness) * Box(
        wall_thickness, length, bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN))
    body += Pos(wall_thickness + channel_width, 0, base_thickness) * Box(
        wall_thickness, length, bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN))
    body -= Pos(clip_width + tab_length / 2.0, length / 2.0, -1.0) * Cylinder(
        4.2 / 2.0, base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body
