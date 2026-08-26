from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """Bench block for upright driver bits.

    shank_diameter: diameter of the bit shank the pockets hold
    columns: number of pockets across the block
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    outer_margin = 2.0
    wall_between_pockets = 2.0
    pocket_diameter = shank_diameter + 0.3
    pitch = pocket_diameter + wall_between_pockets
    pocket_depth = 12.0
    floor_thickness = 3.0
    block_height = floor_thickness + pocket_depth
    rows = 2
    chamfer_size = 0.8

    block_width = (2.0 * outer_margin
                   + columns * pocket_diameter
                   + (columns - 1) * wall_between_pockets)
    block_depth = (2.0 * outer_margin
                   + rows * pocket_diameter
                   + (rows - 1) * wall_between_pockets)

    body = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    first_center = outer_margin + pocket_diameter / 2.0
    for row in range(rows):
        for column in range(columns):
            center_x = first_center + column * pitch
            center_y = first_center + row * pitch
            pocket = Pos(center_x, center_y, floor_thickness) * Cylinder(
                pocket_diameter / 2.0,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - pocket

    # The only dressed edges are the outer top perimeter and the ten pocket
    # mouths.  Selecting all edges wholly in the top plane leaves the bottom
    # perimeter sharp and gives every mouth the same 45-degree lead-in.
    top_edges = [
        edge
        for edge in body.edges()
        if abs(edge.bounding_box().min.Z - block_height) < 1e-7
        and abs(edge.bounding_box().max.Z - block_height) < 1e-7
    ]
    return chamfer(top_edges, length=chamfer_size)
