from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down open channel clip for a cable bundle.

    bundle_diameter: measured width of the taped cable bundle, in mm
    """
    clearance = 0.4
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2.0 * wall
    height = base + channel_depth

    # Channel body: two walls and the floor, then a mounting tab on +X.
    channel_body = Box(body_width, length, height)
    channel_body = channel_body.moved(Location((body_width / 2, length / 2, height / 2)))

    void = Box(channel_width, length + 2.0, channel_depth + 0.02)
    void = void.moved(
        Location((wall + channel_width / 2, length / 2, base + channel_depth / 2 + 0.01))
    )
    clip = channel_body - void

    tab = Box(tab_length, length, base)
    tab = tab.moved(
        Location((body_width + tab_length / 2, length / 2, base / 2))
    )
    clip = clip + tab

    hole = Cylinder(hole_dia / 2, base + 2.0)
    hole = hole.moved(
        Location((body_width + tab_length / 2, length / 2, base / 2))
    )
    clip = clip - hole

    # Square channel, tab-to-wall junction, and the through-hole all stay
    # unchamfered: 1 mm polish on those edges either fills the channel,
    # leaves a concave cosmetic strip, or slivers the wall corners.
    return clip
