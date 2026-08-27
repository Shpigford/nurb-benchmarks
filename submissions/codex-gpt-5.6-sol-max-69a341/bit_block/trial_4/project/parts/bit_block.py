from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """A bench block that stores two rows of driver bits upright.

    shank_diameter: measured width across each round bit shank
    columns: number of bit pockets in each row
    """
    if shank_diameter <= 0.0:
        reject(
            "shank_diameter must be greater than 0 mm",
            param="shank_diameter",
        )
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    clearance = 0.3
    material_between_pockets = 2.0
    material_at_sides = 2.0
    rows = 2
    pocket_depth = 12.0
    floor_thickness = 3.0
    chamfer_size = 0.8

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + material_between_pockets

    block_width = (
        pocket_diameter
        + 2.0 * material_at_sides
        + (columns - 1) * pitch
    )
    block_depth = (
        pocket_diameter
        + 2.0 * material_at_sides
        + (rows - 1) * pitch
    )
    block_height = floor_thickness + pocket_depth

    block = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    first_x = -(columns - 1) * pitch / 2.0
    first_y = -(rows - 1) * pitch / 2.0
    for row in range(rows):
        y = first_y + row * pitch
        for column in range(columns):
            x = first_x + column * pitch
            pocket = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                pocket_depth + chamfer_size,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            block = block - pocket

    tolerance = 1e-6
    top_edges = block.edges().filter_by(
        lambda edge: (
            abs(edge.bounding_box().min.Z - block_height) < tolerance
            and abs(edge.bounding_box().max.Z - block_height) < tolerance
        )
    )
    return chamfer(top_edges, chamfer_size)
