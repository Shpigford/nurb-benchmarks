from nurb import *


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter"))):
    """Screw-down clip with a square channel running along Y.

    bundle_diameter: measured cable bundle width; sets channel width and depth.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than zero", param="bundle_diameter")

    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    length = 12.0
    tab_length = 10.0
    clip_width = channel_width + 2.0 * wall_thickness

    # A single continuous base includes the mounting tab on the +X side.
    body = Box(clip_width + tab_length, length, base_thickness,
               align=(Align.MIN, Align.MIN, Align.MIN))
    for wall_x in (0.0, wall_thickness + channel_width):
        body += Pos(wall_x, 0, base_thickness) * Box(
            wall_thickness, length, bundle_diameter,
            align=(Align.MIN, Align.MIN, Align.MIN))

    body -= Pos(clip_width + tab_length / 2.0, length / 2.0, 0) * Cylinder(
        radius=4.2 / 2.0, height=base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body
