from nurb import *


@part
def bundle_holder(bundle_diameter=float(measured("bundle_diameter")), draft=False):
    """Wall-mounted cable cradle with an accessible screw above the bundle.

    bundle_diameter: measured width of the cable bundle, before fit clearance.
    """
    if bundle_diameter < 4.0:
        reject("Use a bundle diameter of at least 4 mm", param="bundle_diameter")

    length = 12.0
    back_thickness = 3.0
    wall_thickness = 2.4
    opening = bundle_diameter + 0.4
    bundle_height = wall_thickness + opening / 2
    front_height = bundle_height + 1.8
    outside = back_thickness + opening + wall_thickness
    # The complete 8.4 mm driver envelope passes above both cable and lip.
    screw_height = wall_thickness + opening + 6.2
    height = screw_height + 6.8

    back = Pos(0, -length / 2, 0) * Box(
        back_thickness, length, height, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    floor = Pos(0, -length / 2, 0) * Box(
        outside, length, wall_thickness, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    lip = Pos(back_thickness + opening, -length / 2, 0) * Box(
        wall_thickness, length, front_height, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    body = back + floor + lip
    screw = Pos(-1, 0, screw_height) * Rot(0, 90, 0) * Cylinder(
        2.2, back_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    body = body - screw
    if draft:
        return body
    # Keep the seating floor, screw seat and wall interface square. Soften the
    # exposed upper rails without narrowing the cable's clear passage.
    top_edges = body.edges().filter_by(
        lambda edge: (
            abs(edge.center().Z - height) < 0.001
            or (abs(edge.center().Z - front_height) < 0.001
                and abs(edge.center().X - outside) < 0.001)
        )
    )
    return polish(body, top_edges, 1.0)
