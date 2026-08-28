from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A flat, two-row bench block for upright driver bits.

    shank_diameter: measured diameter across a driver-bit shank
    columns: number of bit pockets across the block
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    rows = 2
    clearance = 0.3
    wall = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    block_width = pocket_diameter + 2.0 * wall + (columns - 1) * pitch
    block_depth = pocket_diameter + 2.0 * wall + (rows - 1) * pitch
    block_height = floor_thickness + pocket_depth

    body = Box(block_width, block_depth, block_height)
    top_z = body.bounding_box().max.Z

    # Only the outer top perimeter is softened; the bottom and vertical corners stay sharp.
    top_perimeter = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - top_z) < 0.001
        and abs(edge.bounding_box().max.Z - top_z) < 0.001
    )
    body = chamfer(top_perimeter, lead_in)

    first_x = -block_width / 2.0 + wall + pocket_radius
    first_y = -block_depth / 2.0 + wall + pocket_radius
    pocket_center_z = top_z - pocket_depth / 2.0
    lead_in_center_z = top_z - lead_in / 2.0
    centered = (Align.CENTER, Align.CENTER, Align.CENTER)

    for row in range(rows):
        for column in range(columns):
            x = first_x + column * pitch
            y = first_y + row * pitch
            bore = Pos(x, y, pocket_center_z) * Cylinder(
                pocket_radius, pocket_depth, align=centered
            )
            mouth = Pos(x, y, lead_in_center_z) * Cone(
                pocket_radius, pocket_radius + lead_in, lead_in, align=centered
            )
            body -= bore + mouth

    return body
