from nurb import *


@part
def bundle_holder(bundle_diameter: float = float(measured("bundle_diameter")), draft=False):
    """Wall-mounted cradle with an unobstructed screw seat above the cable.

    bundle_diameter: measured width of the cable bundle, before fit clearance.
    """
    if bundle_diameter < 4.0:
        reject("bundle_diameter must be at least 4 mm", param="bundle_diameter")

    length = 12.8
    back_thickness = 3.0
    wall_thickness = 2.4
    opening = bundle_diameter + 0.4
    front_inside = back_thickness + opening
    depth = front_inside + wall_thickness
    # A circle of radius opening/2 fits at (3 + opening/2, 2.4 + opening/2).
    # The front rises above its centre so an outward translation hits a full wall.
    front_height = wall_thickness + opening / 2 + 2.4
    screw_height = wall_thickness + opening + 5.0
    height = screw_height + 6.2

    back = Box(back_thickness, length, height,
               align=(Align.MIN, Align.CENTER, Align.MIN))
    floor = Box(depth, length, wall_thickness,
                align=(Align.MIN, Align.CENTER, Align.MIN))
    front = Pos(front_inside, 0, 0) * Box(
        wall_thickness, length, front_height,
        align=(Align.MIN, Align.CENTER, Align.MIN))
    body = back + floor + front
    # Axis X; the head seats on the unchamfered plane x=3.0.
    screw = Pos(back_thickness / 2, 0, screw_height) * Cylinder(
        2.2, back_thickness + 2.0, rotation=(0, 90, 0))
    body = body - screw
    if draft:
        return body

    # Only the outer top rails: keep the bed, wall contact, screw seat, and
    # complete cable channel unchanged by the finishing pass.
    edges = body.edges().filter_by(
        lambda e: e.geom_type == GeomType.LINE
        and abs(e.length - length) < 0.001
        and ((abs(e.center().X - depth) < 0.001
              and abs(e.center().Z - front_height) < 0.001)
             or (abs(e.center().X - back_thickness) < 0.001
                 and abs(e.center().Z - height) < 0.001))
    )
    return polish(body, edges, 1.0)
