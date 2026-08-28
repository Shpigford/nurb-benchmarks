from nurb import *


def _box(x0, x1, y0, y1, z0, z1):
    """Create an axis-aligned box from its outside extents."""
    return Box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    )


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter")):
    """Low-material wall clip for one horizontal cable bundle.

    bundle_diameter: measured diameter of the bundle held by the clip.
    """
    # The wall is at minimum X and the print bed is at Z = 0. The 0.4 mm
    # radial fitting allowance is deliberately used in both axes of the U.
    clearance = 0.4
    back_thickness = 2.6
    floor_thickness = 2.6
    front_thickness = 1.6
    length = 18.0
    channel_width = bundle_diameter + 2 * clearance

    front_x0 = back_thickness + channel_width
    front_x1 = front_x0 + front_thickness
    cable_center_z = floor_thickness + bundle_diameter / 2 + clearance

    # A low back web creates the full-length wall reference and joins the
    # floor. A local tall boss gives the M4 head a proper annular seat without
    # carrying a heavy plate across the whole clip.
    back_web = _box(0, back_thickness, 0, length, 0, 12.0)
    screw_seat_depth = 3.0
    screw_boss = _box(0, screw_seat_depth, 2.4, 15.6, 10.2, 22.8)
    floor = _box(0, front_x1, 0, length, 0, floor_thickness)

    # Two opposed guide rails occupy over half the length. Together with the
    # floor they stop a retained bundle translating down or away from the wall,
    # while the middle remains open for the screw head and driver.
    rail_height = cable_center_z + bundle_diameter / 2 + 1.2
    near_rail = _box(front_x0, front_x1, 0, 5.5, 0, rail_height)
    far_rail = _box(front_x0, front_x1, 12.5, length, 0, rail_height)
    body = back_web + screw_boss + floor + near_rail + far_rail

    # The normal counterbore is turned sideways: the 4.4 mm bore enters at
    # the wall, leaves 3.0 mm of seat thickness, then opens to a 9 mm
    # head/driver clearance all the way out of the clip.
    screw_clearance = counterbore(
        4.4, 9.0, front_x1 - screw_seat_depth, front_x1
    ).rotate(Axis.Y, -90).translate((front_x1, length / 2, 16.8))
    body = body - screw_clearance

    # A restrained polish on the top of the boss keeps the public form finished
    # without reducing the cable channel or the flat wall mounting face.
    top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z >= 22.79
    )
    return polish(body, top_edges, 0.6)
