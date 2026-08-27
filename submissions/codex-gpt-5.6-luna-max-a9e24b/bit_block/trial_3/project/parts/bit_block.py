from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """A bench block for storing driver bits upright.

    shank_diameter: diameter of the bit shanks the pockets receive
    columns: number of pockets across the block
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    rows = 2
    pitch = 8.3
    side_material = 2.0
    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    height = floor_thickness + pocket_depth

    width = pocket_diameter + (columns - 1) * pitch + 2.0 * side_material
    depth = pocket_diameter + (rows - 1) * pitch + 2.0 * side_material

    block = Box(width, depth, height, align=(Align.MIN, Align.MIN, Align.MIN))
    top_edges = block.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > height - 1e-6
        and edge.bounding_box().max.Z > height - 1e-6
    )
    block = chamfer(top_edges, length=lead_in)

    first_x = side_material + pocket_radius
    first_y = side_material + pocket_radius
    for column in range(columns):
        for row in range(rows):
            x = first_x + column * pitch
            y = first_y + row * pitch

            straight_pocket = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            mouth = Pos(x, y, height - lead_in) * Cone(
                pocket_radius,
                pocket_radius + lead_in,
                lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            block = block - (straight_pocket + mouth)

    return block
