"""Square, open cable channel with a screw-down mounting tab."""

from nurb import *


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter"))):
    """Hold a cable bundle in a full-length, open-top channel.

    bundle_diameter: measured width of the cable bundle; sets channel width and depth.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than zero", param="bundle_diameter")

    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_width = 4.2
    clip_width = channel_width + 2.0 * wall_thickness

    # The channel is centered on X; the tab projects from the right-hand wall.
    base = Pos(tab_length / 2.0, 0, 0) * Box(
        clip_width + tab_length, part_length, base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    wall_offset = (channel_width + wall_thickness) / 2.0
    body = base
    for side in (-1, 1):
        body += Pos(side * wall_offset, 0, base_thickness) * Box(
            wall_thickness, part_length, bundle_diameter,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    body -= Pos(clip_width / 2.0 + tab_length / 2.0, 0, -1.0) * Cylinder(
        screw_hole_width / 2.0, base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Preserve the specified square channel and constant wall/base dimensions.
    return body
