from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that traps a cable bundle running along the wall.

    bundle_diameter: calipered width of the taped cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            "bundle_diameter under 4mm is too small for a printable clip",
            param="bundle_diameter",
        )

    length = 16.0
    end = 3.2
    back_t = 2.6
    wall = 2.4
    hole_d = 4.4
    pocket_d = bundle_diameter + 0.4
    pocket_r = pocket_d / 2

    screw_z = 5.2
    cx = back_t + 0.6 + pocket_r
    cz = 12.0
    front_x = cx + pocket_r + wall
    height = cz + pocket_r + wall

    def placed_box(dx, dy, dz, x, y, z):
        return Box(dx, dy, dz, align=(Align.MIN, Align.MIN, Align.MIN)).locate(
            Location((x, y, z))
        )

    body = placed_box(front_x, end, height, 0, 0, 0)
    body += placed_box(front_x, end, height, 0, length - end, 0)
    body += placed_box(back_t, length, height, 0, 0, 0)

    trough = Cylinder(
        pocket_r,
        length + 4,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
        rotation=(90, 0, 0),
    ).locate(Location((cx, length / 2, cz)))
    opening = Box(
        pocket_d,
        length + 4,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).locate(Location((cx, length / 2, cz)))
    body -= trough + opening

    screw = Cylinder(
        hole_d / 2,
        back_t + 4,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
        rotation=(0, 90, 0),
    ).locate(Location((back_t / 2, length / 2, screw_z)))
    body -= screw

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    # Only the long outer uprights: 1mm polish here does not nibble the trough.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.2
        and e.bounding_box().min.X > back + 0.2
        and e.length > 8.0
    )
    return polish(body, keep, 1.0)
