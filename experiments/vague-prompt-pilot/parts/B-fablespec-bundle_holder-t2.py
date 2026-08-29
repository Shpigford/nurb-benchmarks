from nurb import *


@part
def bundle_holder(draft=False):
    """Wall-mount J-channel for a taped cable bundle.

    Slot, lip, floor reach, back-plate height, and screw height all follow
    bundle_diameter from measurements.toml.
    """
    d = measured("bundle_diameter")
    c = 0.4
    back = 4.0
    floor = 3.0
    lip = 3.0
    width = 12.0
    slot = d + c
    outer_x = back + slot + lip
    height = floor + slot + 12.6
    lip_top = floor + 0.75 * d
    hole_z = floor + slot + 6.6
    hole_dia = 4.5
    lead = 1.5

    profile = Polygon(
        (0, 0),
        (outer_x, 0),
        (outer_x, lip_top),
        (outer_x - lip, lip_top),
        (outer_x - lip, floor),
        (back, floor),
        (back, height),
        (0, height),
    )
    body = extrude(profile, -width)
    body = body.rotate(Axis((0, 0, 0), (1, 0, 0)), 90)

    circ = Circle(hole_dia / 2)
    hole = extrude(circ, back + 2)
    hole = hole.rotate(Axis((0, 0, 0), (0, 1, 0)), 90)
    hole = hole.translate(Vector(-1, width / 2, hole_z))
    body = body - hole

    if draft:
        return body

    def lead_in(e):
        mid = e.center()
        along_y = abs(e.length - width) < 0.3
        if not along_y:
            return False
        lip_inner = abs(mid.X - (back + slot)) < 0.2 and abs(mid.Z - lip_top) < 0.2
        mouth = abs(mid.X - back) < 0.2 and abs(mid.Z - height) < 0.2
        return lip_inner or mouth

    return chamfer(body.edges().filter_by(lead_in), lead)
