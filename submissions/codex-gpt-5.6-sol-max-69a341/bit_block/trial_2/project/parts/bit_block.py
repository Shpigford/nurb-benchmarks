from nurb import *


@part
def bit_block(
    shank_diameter: float = 6.0,
    columns: int = 5,
):
    """A compact bench block that holds two rows of driver bits upright.

    shank_diameter: measured width of each driver's round shank
    columns: number of bit pockets in each row
    """
    pocket_diameter = shank_diameter + 0.3
    pocket_spacing = 2.0
    side_wall = 2.0
    rows = 2
    pitch = pocket_diameter + pocket_spacing

    block_width = pocket_diameter + 2 * side_wall + (columns - 1) * pitch
    block_depth = pocket_diameter + 2 * side_wall + (rows - 1) * pitch
    block_height = 15.0

    pocket_depth = 12.0
    floor_thickness = 3.0
    chamfer_size = 0.8

    body = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    pocket_radius = pocket_diameter / 2
    first_center = side_wall + pocket_radius
    for row in range(rows):
        for column in range(columns):
            center_x = first_center + column * pitch
            center_y = first_center + row * pitch

            straight_pocket = Pos(center_x, center_y, floor_thickness) * Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            lead_in = Pos(
                center_x,
                center_y,
                block_height - chamfer_size,
            ) * Cone(
                pocket_radius,
                pocket_radius + chamfer_size,
                chamfer_size,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - straight_pocket - lead_in

    top_outer_edges = (
        body.edges()
        .filter_by(GeomType.LINE)
        .filter_by_position(Axis.Z, block_height, block_height)
    )
    body = chamfer(top_outer_edges, length=chamfer_size)

    return body
