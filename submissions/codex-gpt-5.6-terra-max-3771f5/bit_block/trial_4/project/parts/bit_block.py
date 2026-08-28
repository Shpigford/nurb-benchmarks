from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A compact bench block for driver bits.

    shank_diameter: measured width of each bit shank.
    columns: number of bit pockets across the block.
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than zero", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    clearance = 0.3
    wall = 2.0
    floor_thickness = 3.0
    pocket_depth = 12.0
    lead_in = 0.8

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    height = floor_thickness + pocket_depth
    length = 2.0 * wall + pocket_diameter + (columns - 1) * pitch
    width = 2.0 * wall + pocket_diameter + pitch

    body = Box(length, width, height, align=(Align.MIN, Align.MIN, Align.MIN))
    top_perimeter = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > height - 0.001
    )
    body = chamfer(top_perimeter, lead_in)

    for row in range(2):
        for column in range(columns):
            x = wall + pocket_radius + column * pitch
            y = wall + pocket_radius + row * pitch
            straight_pocket = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            mouth_lead_in = Pos(x, y, height - lead_in) * Cone(
                pocket_radius,
                pocket_radius + lead_in,
                lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - straight_pocket - mouth_lead_in

    return body
