from nurb import *


# Keep the file's measured value as the default while leaving the diameter as a
# normal float parameter in the part API.
DEFAULT_BUNDLE_DIAMETER = measured("bundle_diameter")


@part
def bundle_holder(bundle_diameter=DEFAULT_BUNDLE_DIAMETER, draft=False):
    """A one-screw wall clip for a horizontal cable bundle.

    bundle_diameter: measured diameter of the cable bundle held in the channel.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    # The channel gives the measured bundle 0.4 mm clearance at each supporting
    # surface. Its rectangular opening is deliberately open above, so the cable
    # can be dropped in while the floor and front rail arrest down/outward motion.
    side_clearance = 0.4
    back_thickness = 3.6
    floor_thickness = 2.6
    front_rail_thickness = 2.4
    part_length = 13.0

    cavity_radius = bundle_diameter / 2.0 + side_clearance
    cable_center_x = back_thickness + cavity_radius
    cable_center_z = floor_thickness + cavity_radius
    front_rail_inner_x = cable_center_x + cavity_radius
    front_rail_height = cable_center_z + 1.0
    front_outer_x = front_rail_inner_x + front_rail_thickness

    # The pan-head / driver clearance sits above the bundle. A 2.5 mm-deep
    # shank bore remains between the wall and the 8.4 mm virtual head seat.
    screw_bore_radius = 2.2
    head_clearance_radius = 4.3  # 0.1 mm radial clearance around the 8.4 mm driver
    head_seat_x = 2.5
    screw_y = part_length / 2.0
    screw_z = cable_center_z + bundle_diameter / 2.0 + head_clearance_radius + 0.4
    back_height = screw_z + head_clearance_radius + 2.4

    back = Pos(back_thickness / 2.0, part_length / 2.0, back_height / 2.0) * Box(
        back_thickness, part_length, back_height
    )
    floor = Pos(front_outer_x / 2.0, part_length / 2.0, floor_thickness / 2.0) * Box(
        front_outer_x, part_length, floor_thickness
    )
    front_rail = Pos(
        front_rail_inner_x + front_rail_thickness / 2.0,
        part_length / 2.0,
        front_rail_height / 2.0,
    ) * Box(front_rail_thickness, part_length, front_rail_height)

    # Cylinders are center-aligned along their axis. Rotate them to the
    # wall-normal +X axis, then explicitly span the back and the head recess.
    shank_bore = Pos(back_thickness / 2.0, screw_y, screw_z) * Cylinder(
        screw_bore_radius, back_thickness + 0.2, rotation=(0, 90, 0)
    )
    head_clearance_end_x = back_thickness + 0.2
    head_clearance = Pos(
        (head_seat_x + head_clearance_end_x) / 2.0, screw_y, screw_z
    ) * Cylinder(
        head_clearance_radius,
        head_clearance_end_x - head_seat_x,
        rotation=(0, 90, 0),
    )
    back = back - shank_bore - head_clearance

    body = back + floor + front_rail
    if draft:
        return body

    # Only the exposed top-front edge of the mounting spine is polished. The
    # channel, wall face, bed face, and all concave junctions stay dimensionally sharp.
    top_front = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > back_height - 0.01
        and e.bounding_box().min.X > back_thickness - 0.01
    )
    return polish(body, top_front, 1.0)
