from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Upright driver-bit block.

    shank_diameter: diameter of the bit shank the pockets accept
    columns: number of pockets across the block
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    block_height = floor_thickness + pocket_depth
    wall_between_pockets = 2.0
    side_margin = 2.0
    rows = 2
    pitch = pocket_diameter + wall_between_pockets

    block_width = 2.0 * side_margin + columns * pocket_diameter + (columns - 1) * wall_between_pockets
    block_depth = 2.0 * side_margin + rows * pocket_diameter + (rows - 1) * wall_between_pockets

    block = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    for column in range(columns):
        for row in range(rows):
            x = side_margin + pocket_radius + column * pitch
            y = side_margin + pocket_radius + row * pitch
            pocket = Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).located(Location((x, y, floor_thickness)))
            block = block - pocket

    if draft:
        return block

    top_edges = block.edges().filter_by(
        lambda edge: (
            edge.bounding_box().min.Z > block_height - 1e-6
            and edge.bounding_box().max.Z < block_height + 1e-6
        )
    )
    return chamfer(top_edges, length=0.8)
