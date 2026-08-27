from build123d import Align, Box, Cylinder, Pos
from nurb import part


@part
def bundle_holder(bundle_diameter: float = 8.0):
    """Wall-mounted, thread-through holder for a horizontal cable bundle.

    bundle_diameter: measured width of the cable bundle held by the tunnel
    """
    cable_clearance = 0.4
    passage_size = bundle_diameter + cable_clearance

    holder_length = 12.0
    wall_plate_thickness = 3.0
    retaining_wall_thickness = 1.6
    screw_hole_width = 4.4

    tunnel_height = passage_size + 2.0 * retaining_wall_thickness
    holder_depth = wall_plate_thickness + passage_size + retaining_wall_thickness
    plate_height = tunnel_height + 10.2

    minimum_corner = (Align.MIN, Align.MIN, Align.MIN)
    tunnel = Box(
        holder_depth,
        holder_length,
        tunnel_height,
        align=minimum_corner,
    )
    cable_passage = Pos(
        wall_plate_thickness,
        -1.0,
        retaining_wall_thickness,
    ) * Box(
        passage_size,
        holder_length + 2.0,
        passage_size,
        align=minimum_corner,
    )
    tunnel = tunnel - cable_passage

    upper_plate = Pos(0, 0, tunnel_height) * Box(
        wall_plate_thickness,
        holder_length,
        plate_height - tunnel_height,
        align=minimum_corner,
    )

    screw_z = tunnel_height + (plate_height - tunnel_height) / 2.0
    screw_bore = Pos(-1.0, holder_length / 2.0, screw_z) * Cylinder(
        screw_hole_width / 2.0,
        wall_plate_thickness + 2.0,
        rotation=(0, 90, 0),
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    )

    return tunnel + upper_plate - screw_bore
