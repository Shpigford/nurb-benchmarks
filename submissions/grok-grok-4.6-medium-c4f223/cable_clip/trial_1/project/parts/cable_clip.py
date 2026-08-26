from nurb import *

WALL = 2.4
BASE = 3.0
LENGTH = 12.0
TAB_LENGTH = 10.0
HOLE_DIAMETER = 4.2
CHANNEL_CLEARANCE = 0.4


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter")), draft=False):
    """Screw-down clip that holds a cable bundle in an open channel.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    if bundle_diameter <= 0:
        reject(
            "bundle_diameter must be greater than 0 so the channel has depth",
            param="bundle_diameter",
        )

    channel_width = bundle_diameter + CHANNEL_CLEARANCE
    channel_depth = bundle_diameter
    height = BASE + channel_depth
    channel_span = channel_width + 2 * WALL

    body = Box(channel_span, LENGTH, height, align=(Align.MIN, Align.MIN, Align.MIN))
    channel = Box(
        channel_width,
        LENGTH + 2,
        channel_depth + 1,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).move(Location((WALL, -1, BASE)))
    body = body - channel

    tab = Box(
        TAB_LENGTH, LENGTH, BASE, align=(Align.MIN, Align.MIN, Align.MIN)
    ).move(Location((channel_span, 0, 0)))
    hole = Cylinder(HOLE_DIAMETER / 2, BASE + 2).move(
        Location((channel_span + TAB_LENGTH / 2, LENGTH / 2, BASE / 2))
    )
    clip = body + tab - hole

    if draft:
        return clip
    # Channel interior stays square: no chamfer or fillet on the floor or inner walls.
    # Outer polish is skipped so 1mm corner triangles do not become slivers.
    return clip
