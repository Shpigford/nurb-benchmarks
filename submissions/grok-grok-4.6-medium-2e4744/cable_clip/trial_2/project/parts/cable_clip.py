from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down clip that holds a cable bundle against a surface.

    bundle_diameter: calipered width of the taped cable bundle the channel holds
    """
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2
    extra = 0.4

    channel_width = bundle_diameter + extra
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall

    # One base plate: channel floor and mounting tab, flush on the bed.
    plate = Box(body_width + tab_length, length, base)
    plate = plate.translate((tab_length / 2, 0, base / 2))

    left = Box(wall, length, channel_depth)
    left = left.translate(
        (-(channel_width / 2 + wall / 2), 0, base + channel_depth / 2)
    )
    right = Box(wall, length, channel_depth)
    right = right.translate(
        (channel_width / 2 + wall / 2, 0, base + channel_depth / 2)
    )
    clip = plate + left + right

    hole_x = body_width / 2 + tab_length / 2
    bore = Cylinder(hole_dia / 2, base + 2).translate((hole_x, 0, base / 2))
    clip = clip - bore

    if draft:
        return clip

    # Square channel: never chamfer inside the U or on the bed. Only the long
    # outer rims parallel to the cable are polished, so meeting chamfers cannot
    # leave sub-1mm2 corner faces or thin the 2.4mm walls.
    bed = clip.bounding_box().min.Z
    half = channel_width / 2
    inner = concave_edges(clip)

    def keep(e):
        if e in inner:
            return False
        if e.geom_type != GeomType.LINE:
            return False
        bb = e.bounding_box()
        if bb.min.Z <= bed + 1e-4:
            return False
        if bb.max.Y - bb.min.Y < length - 1e-3:
            return False
        c = bb.center()
        if abs(c.X) <= half + 1e-3 and c.Z >= base - 1e-3:
            return False
        return True

    return polish(clip, clip.edges().filter_by(keep), 1.0)
