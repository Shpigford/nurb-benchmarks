from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
):
    """A bench block that stores driver bits upright.

    shank_diameter: measured width of each bit's round shank
    columns: number of pockets across the block
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

    rows = 2
    clearance = 0.3
    wall = 2.0
    floor = 3.0
    pocket_depth = 12.0
    chamfer_size = 0.8

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    width = (columns - 1) * pitch + pocket_diameter + 2.0 * wall
    depth = (rows - 1) * pitch + pocket_diameter + 2.0 * wall
    height = floor + pocket_depth

    block = Box(
        width,
        depth,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Preserve the full, sharp bottom perimeter and chamfer only the four
    # outer edges that bound the top face.
    top_edges = block.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7
    )
    block = chamfer(top_edges, chamfer_size)

    # A straight cylinder establishes the exact pocket diameter, depth, and
    # flat floor.  The coaxial 45-degree frustum adds only the mouth lead-in.
    for row in range(rows):
        y = (row - (rows - 1) / 2.0) * pitch
        for column in range(columns):
            x = (column - (columns - 1) / 2.0) * pitch
            pocket = Pos(x, y, floor) * Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            lead_in = Pos(x, y, height - chamfer_size) * Cone(
                pocket_radius,
                pocket_radius + chamfer_size,
                chamfer_size,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            block = block - pocket - lead_in

    return block
