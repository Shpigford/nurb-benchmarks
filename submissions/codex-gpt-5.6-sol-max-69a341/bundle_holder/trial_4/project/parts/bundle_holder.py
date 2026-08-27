from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Hold a horizontal cable bundle against a wall with one M4 screw.

    bundle_diameter: measured width across the cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            "bundle_diameter under 4mm leaves too little room for this holder's M4 mount",
            param="bundle_diameter",
        )

    length = 12.0
    fit_clearance = 0.4
    clear_width = bundle_diameter + fit_clearance

    back_thickness = 3.0
    floor_thickness = 2.4
    lip_thickness = 2.4

    cable_center_z = floor_thickness + clear_width / 2
    lip_height = cable_center_z + bundle_diameter / 4

    # Keep the M4 pan head completely above the retained cable envelope.
    screw_hole_width = 4.4
    screw_head_width = 8.4
    screw_center_z = (
        cable_center_z + bundle_diameter / 2 + screw_head_width / 2 + 0.8
    )
    back_height = screw_center_z + screw_head_width / 2 + 0.8

    front_inside_x = back_thickness + clear_width
    overall_depth = front_inside_x + lip_thickness

    from_corner = (Align.MIN, Align.MIN, Align.MIN)
    back = Box(back_thickness, length, back_height, align=from_corner)
    floor = Box(overall_depth, length, floor_thickness, align=from_corner)
    front_lip = Pos(front_inside_x, 0, 0) * Box(
        lip_thickness, length, lip_height, align=from_corner
    )

    holder = back + floor + front_lip

    # The bore opens at the wall face and exits the 3mm back at the head seat.
    screw_bore = (
        Pos(-0.1, length / 2, screw_center_z)
        * Rot(Y=90)
        * Cylinder(
            screw_hole_width / 2,
            back_thickness + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    holder = holder - screw_bore

    if draft:
        return holder

    # Soften only the handled outside of the retaining lip. The bed, wall,
    # channel, and screw-seat edges remain dimensionally exact.
    def exposed_front_lip(edge):
        bounds = edge.bounding_box()
        lies_on_front = (
            abs(bounds.min.X - overall_depth) < 0.01
            and abs(bounds.max.X - overall_depth) < 0.01
        )
        lies_on_bed = abs(bounds.min.Z) < 0.01 and abs(bounds.max.Z) < 0.01
        return lies_on_front and not lies_on_bed

    lip_edges = holder.edges().filter_by(exposed_front_lip)
    return polish(holder, lip_edges, 1.0)
