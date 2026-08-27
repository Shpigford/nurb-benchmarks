from nurb import *


@part
def bit_block(shank_diameter: float = 6.0, columns: int = 5):
    """Bench block that holds two rows of driver bits upright.

    shank_diameter: measured diameter across each driver-bit shank
    columns: number of bit pockets in each of the two rows
    """
    if columns < 1:
        raise ValueError("columns must be at least 1")
    if shank_diameter <= 0:
        raise ValueError("shank_diameter must be positive")

    clearance = 0.3
    wall = 2.0
    side_material = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    chamfer_size = 0.8
    rows = 2

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    width = columns * pitch + 2.0
    depth = rows * pitch + 2.0
    height = pocket_depth + floor_thickness

    body = Box(width, depth, height)
    top_outer_edges = body.edges().sort_by(Axis.Z)[-4:]
    body = chamfer(top_outer_edges, length=chamfer_size)

    pocket_center_z = height / 2.0 - pocket_depth / 2.0
    lead_in_center_z = height / 2.0 - chamfer_size / 2.0
    first_x = -width / 2.0 + side_material + pocket_radius
    first_y = -depth / 2.0 + side_material + pocket_radius

    cutters = None
    for row in range(rows):
        y = first_y + row * pitch
        for column in range(columns):
            x = first_x + column * pitch
            straight_pocket = Pos(x, y, pocket_center_z) * Cylinder(
                pocket_radius, pocket_depth
            )
            lead_in = Pos(x, y, lead_in_center_z) * Cone(
                pocket_radius,
                pocket_radius + chamfer_size,
                chamfer_size,
            )
            cutter = straight_pocket + lead_in
            cutters = cutter if cutters is None else cutters + cutter

    return body - cutters
