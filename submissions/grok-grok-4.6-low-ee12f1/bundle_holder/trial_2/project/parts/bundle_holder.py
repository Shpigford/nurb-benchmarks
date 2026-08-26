from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall-mounted clip for a cable bundle that runs along the wall.

    bundle_diameter: measured width of the taped cable bundle
    """
    wall = 2.4
    fit = 0.4
    seat = bundle_diameter + fit
    length = 12.0
    screw_hole = 4.4
    head = 8.4
    around = 2.4
    radius = seat / 2.0

    channel_h = wall + seat
    screw_z = channel_h + around + head / 2.0
    plate_h = screw_z + screw_hole / 2.0 + around
    depth = wall + seat + wall
    cx = wall + radius
    cz = wall + radius

    back = Box(wall, length, plate_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    cradle = Box(depth, length, channel_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    body = back + cradle

    tunnel = (
        Cylinder(radius, length + 4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        .rotate(Axis.X, 90)
        .moved(Location((cx, 0, cz)))
    )
    slot = Box(
        seat,
        length + 4.0,
        radius + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((cx, 0, cz)))
    body = body - tunnel - slot

    screw = (
        Cylinder(
            screw_hole / 2,
            wall + 20.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.Y, 90)
        .moved(Location((wall / 2, 0, screw_z)))
    )
    body = body - screw

    if draft:
        return body

    bed = body.bounding_box().min.Z
    bb = body.bounding_box()

    def polish_edge(e):
        ebb = e.bounding_box()
        if ebb.min.Z <= bed + 0.05 or ebb.min.X <= 0.05:
            return False
        if e.geom_type != GeomType.LINE:
            return False
        mid_x = (ebb.min.X + ebb.max.X) / 2
        mid_z = (ebb.min.Z + ebb.max.Z) / 2
        if wall < mid_x < wall + seat and mid_z > wall:
            return False
        if ebb.max.Z > channel_h - 0.2 and ebb.max.X > bb.max.X - 0.2:
            return False
        return (
            abs(ebb.max.X - bb.max.X) < 0.08
            or abs(ebb.max.Z - bb.max.Z) < 0.08
            or abs(ebb.max.Y - bb.max.Y) < 0.08
            or abs(ebb.min.Y - bb.min.Y) < 0.08
        )

    keep = body.edges().filter_by(polish_edge)
    return polish(body, keep, 1.0)
