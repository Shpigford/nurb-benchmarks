from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall holder for a horizontal cable bundle.

    bundle_diameter: measured outside diameter of the cable bundle
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    # The cable is held in a deliberately open channel.  The wall supplies the
    # fourth side, while the printed floor and front rail provide the two
    # restraints that matter when the cable is pulled down or outward.
    length = 16.0
    back_thickness = 3.0
    floor_thickness = 2.4
    rail_thickness = 3.0
    fit_clearance = 0.4

    cable_radius = bundle_diameter / 2.0
    cable_x = back_thickness + cable_radius + fit_clearance
    cable_z = floor_thickness + cable_radius + fit_clearance
    rail_inner_x = cable_x + cable_radius + fit_clearance
    rail_top_z = cable_z + cable_radius + fit_clearance
    floor_length = rail_inner_x + rail_thickness

    floor = Box(
        floor_length,
        length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    rail = Pos(rail_inner_x, 0, 0) * Box(
        rail_thickness,
        length,
        rail_top_z,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # A wide, tall spine gives the wall a generous flat contact patch.  It is
    # behind the cable path and also leaves room for a proper screw-head seat.
    mount_width = 10.0
    mount_y = (length - mount_width) / 2.0
    head_radius = 4.2  # 8.4 mm driver/head clearance cylinder
    screw_z = cable_z + cable_radius + head_radius + 0.6
    tower_top_z = screw_z + head_radius + 1.2
    tower = Pos(0, mount_y, 0) * Box(
        back_thickness,
        mount_width,
        tower_top_z,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = floor + rail + tower

    # The shank bore opens on the wall side.  Its 2.4 mm depth ends at a flat
    # annular seat; the larger pocket then opens toward +X for the head/driver.
    seat_x = 2.4
    bore = Pos(0, length / 2.0, screw_z) * Cylinder(
        2.2,
        seat_x,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    head_pocket = Pos(seat_x, length / 2.0, screw_z) * Cylinder(
        head_radius,
        back_thickness - seat_x + 0.2,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - bore - head_pocket

    if draft:
        return body

    # Polish one exposed, non-mating rail edge.  The channel edge, bed edges,
    # back edges, and screw seat remain exact fit geometry.
    def exposed_rail_top(edge):
        bb = edge.bounding_box()
        return (
            bb.min.Z > rail_top_z - 0.01
            and bb.max.X > floor_length - 0.01
            and bb.max.Y - bb.min.Y > length - 0.1
        )

    return polish(body, body.edges().filter_by(exposed_rail_top), 1.0)
