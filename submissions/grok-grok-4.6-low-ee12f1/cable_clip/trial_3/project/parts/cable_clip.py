from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down clip for a taped cable bundle.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    clearance = 0.4
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    tab_thickness = 3.0
    hole_dia = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    height = base + channel_depth
    outer_w = channel_width + 2 * wall

    body = Box(outer_w, length, height).moved(
        Location((outer_w / 2, length / 2, height / 2))
    )
    tab = Box(tab_length, length, tab_thickness).moved(
        Location((outer_w + tab_length / 2, length / 2, tab_thickness / 2))
    )
    clip = body + tab

    void = Box(channel_width, length + 2, channel_depth).moved(
        Location((wall + channel_width / 2, length / 2, base + channel_depth / 2))
    )
    hole = Cylinder(hole_dia / 2, tab_thickness + 2).moved(
        Location((outer_w + tab_length / 2, length / 2, tab_thickness / 2))
    )
    clip = clip - void - hole

    if draft:
        return clip

    # Channel floor and inner corners must stay square. Outer 1mm polish is
    # kept off the tab–wall junction (concave) and off the hole rim so the
    # 3mm tab does not go under min_wall.
    bed = clip.bounding_box().min.Z
    inner_x0 = wall
    inner_x1 = wall + channel_width
    hole_x = outer_w + tab_length / 2

    def skip(e):
        mid = e.center()
        if e.bounding_box().min.Z <= bed + 0.02:
            return True
        if inner_x0 - 0.05 <= mid.X <= inner_x1 + 0.05 and mid.Z > bed + 0.05:
            return True
        if abs(mid.X - hole_x) < hole_dia / 2 + 0.6:
            return True
        if abs(mid.X - outer_w) < 0.2:
            return True
        return False

    keep = clip.edges().filter_by(lambda e: not skip(e))
    return polish(clip, keep, 1.0)
