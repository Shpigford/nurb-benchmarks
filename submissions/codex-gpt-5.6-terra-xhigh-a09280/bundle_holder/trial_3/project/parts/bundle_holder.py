from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall-mounted cable-bundle clip with one M4 pan-head mounting screw.

    bundle_diameter: measured diameter of the cable bundle held by the clip.
    """
    # The cable path has 0.4 mm of total diameter clearance. The bottom and
    # front rails deliberately leave the back open: the wall is the rear stop.
    clearance = 0.4
    pocket_radius = bundle_diameter / 2.0 + clearance / 2.0
    base_thickness = 2.4
    rail_thickness = 2.4
    holder_length = 16.0
    wall_spine_thickness = 1.0

    # The 1 mm wall spine is safely behind the cable: the actual 8 mm bundle
    # still has 0.4 mm of space to it, and the spine grounds the screw plate.
    cable_center_x = wall_spine_thickness + pocket_radius + clearance / 2.0
    cable_center_z = base_thickness + pocket_radius + clearance
    front_inner_x = cable_center_x + pocket_radius + clearance
    bridge_z = cable_center_z + pocket_radius + clearance
    bridge_thickness = 2.4

    # The pan head seats on the room-side face after 2.6 mm of shank path.
    # From that face forward, the 8.4 mm head and driver are in open air.
    screw_hole_radius = 2.2
    screw_seat_x = 2.6
    plate_depth = screw_seat_x
    screw_y = holder_length / 2.0
    screw_head_radius = 4.3
    screw_z = bridge_z + screw_head_radius + 1.0
    plate_top = screw_z + screw_head_radius + 1.2

    def box(x, y, z, at):
        return Pos(*at) * Box(x, y, z, align=(Align.MIN, Align.MIN, Align.MIN))

    # The rails share the full cable run. Their positions give the 8 mm bundle
    # at least 0.4 mm to move before meeting the wall, bottom, or front rail.
    base = box(front_inner_x + rail_thickness, holder_length, base_thickness, (0, 0, 0))
    wall_spine = box(wall_spine_thickness, holder_length, bridge_z, (0, 0, 0))
    front_rail = box(
        rail_thickness,
        holder_length,
        bridge_z - base_thickness,
        (front_inner_x, 0, base_thickness),
    )
    mounting_plate = box(
        plate_depth,
        holder_length,
        plate_top - bridge_z,
        (0, 0, bridge_z),
    )

    # Two end bridges make this one solid while keeping the centerline clear
    # for the full 8.4 mm screw-head and driver envelope.
    end_band = 3.0
    # Small overlaps are intentional: touching faces alone are separate solids
    # to the boolean kernel, while these 0.1 mm laps fuse the frame.
    bridge_start_x = plate_depth - 0.1
    bridge_length = front_inner_x - plate_depth + 0.2
    left_bridge = box(bridge_length, end_band, bridge_thickness, (bridge_start_x, 0, bridge_z))
    right_bridge = box(
        bridge_length, end_band, bridge_thickness,
        (bridge_start_x, holder_length - end_band, bridge_z),
    )

    body = base + wall_spine + front_rail + mounting_plate + left_bridge + right_bridge

    # Horizontal 4.4 mm M4 clearance bore. The pan head begins at the front
    # face, so its full 8.4 mm driver envelope is clear in +X.
    shank = (
        Pos(screw_seat_x, screw_y, screw_z)
        * Rot(0, -90, 0)
        * Cylinder(screw_hole_radius, screw_seat_x, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
    return body - shank
