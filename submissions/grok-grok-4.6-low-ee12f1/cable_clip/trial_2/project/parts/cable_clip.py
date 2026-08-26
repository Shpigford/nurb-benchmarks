from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down clip that holds a cable bundle along Y.

    bundle_diameter: measured width of the cable bundle, in mm
    """
    bundle_diameter = float(bundle_diameter)

    clearance = 0.4
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    height = base + channel_depth
    body_width = channel_width + 2 * wall

    body = Box(body_width, length, height).moved(
        Location((body_width / 2, length / 2, height / 2))
    )
    tab = Box(tab_length, length, base).moved(
        Location((body_width + tab_length / 2, length / 2, base / 2))
    )
    clip = body + tab

    channel = Box(channel_width, length + 2, channel_depth + 1).moved(
        Location(
            (
                wall + channel_width / 2,
                length / 2,
                base + (channel_depth + 1) / 2,
            )
        )
    )
    clip = clip - channel

    hole = Cylinder(hole_dia / 2, base + 2).moved(
        Location((body_width + tab_length / 2, length / 2, base / 2))
    )
    clip = clip - hole

    if draft:
        return clip
    return clip
