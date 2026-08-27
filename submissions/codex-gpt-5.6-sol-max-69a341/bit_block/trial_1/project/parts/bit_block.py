from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that stores two rows of driver bits upright.

    shank_diameter: measured diameter across each bit's round shank
    columns: number of bit pockets in each of the two rows
    """
    if shank_diameter <= 0.0:
        reject(
            "shank_diameter must be greater than 0 mm",
            param="shank_diameter",
        )
    if columns < 1:
        reject(
            "columns must be at least 1",
            param="columns",
        )

    clearance = 0.3
    wall = 2.0
    floor = 3.0
    pocket_depth = 12.0
    chamfer_size = 0.8
    rows = 2

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    block_width = columns * pocket_diameter + (columns - 1) * wall + 2.0 * wall
    block_depth = rows * pocket_diameter + (rows - 1) * wall + 2.0 * wall
    block_height = floor + pocket_depth

    body = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Only the four top outside edges are dressed; the vertical corners and the
    # entire bed-contact perimeter remain sharp.
    top_outer_edges = body.edges().sort_by(Axis.Z)[-4:]
    body = chamfer(top_outer_edges, chamfer_size)

    first_center = wall + pocket_radius
    for row in range(rows):
        center_y = first_center + row * pitch
        for column in range(columns):
            center_x = first_center + column * pitch

            # The cylindrical cut establishes the exact flat-bottomed 12 mm
            # pocket. The coaxial frustum adds only the requested 45-degree
            # lead-in over the top 0.8 mm.
            pocket = Pos(center_x, center_y, floor) * Cylinder(
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
            body = body - pocket - lead_in

    return body
