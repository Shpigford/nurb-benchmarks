from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """A compact bench block that stores two rows of driver bits upright.

    shank_diameter: measured width of each driver's round shank
    columns: number of bit pockets in each of the two rows
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    clearance = 0.3
    material_between_pockets = 2.0
    side_material = 2.0
    rows = 2
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + material_between_pockets
    width = columns * pocket_diameter + (columns - 1) * material_between_pockets + 2.0 * side_material
    depth = rows * pocket_diameter + (rows - 1) * material_between_pockets + 2.0 * side_material
    height = pocket_depth + floor_thickness

    block = Box(
        width,
        depth,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_outer_edges = block.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z >= height - 1e-7
    )
    block = chamfer(top_outer_edges, length=lead_in)

    pocket = Cylinder(
        pocket_radius,
        pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    mouth = Pos(0, 0, pocket_depth - lead_in) * Cone(
        pocket_radius,
        pocket_radius + lead_in,
        lead_in,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = pocket + mouth

    x_start = -0.5 * (columns - 1) * pitch
    y_start = -0.5 * (rows - 1) * pitch
    for column in range(columns):
        for row in range(rows):
            cutter = Pos(
                x_start + column * pitch,
                y_start + row * pitch,
                floor_thickness,
            ) * pocket
            block = block - cutter

    return block
