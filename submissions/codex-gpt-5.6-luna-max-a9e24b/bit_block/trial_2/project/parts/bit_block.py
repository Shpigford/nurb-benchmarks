from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """Bench block for upright driver bits.

    shank_diameter: diameter of the bit shanks in millimetres
    columns: number of pocket columns along the long side
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")

    pitch = 8.3
    side_margin = 2.0
    row_count = 2
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    height = floor_thickness + pocket_depth
    pocket_diameter = shank_diameter + 0.3

    block_width = 2.0 * side_margin + pocket_diameter + (columns - 1) * pitch
    block_depth = 2.0 * side_margin + pocket_diameter + (row_count - 1) * pitch

    body = Box(
        block_width,
        block_depth,
        height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > height - 1e-6
    )
    body = chamfer(top_edges, length=lead_in)

    straight_depth = pocket_depth - lead_in
    for row in range(row_count):
        center_y = side_margin + pocket_diameter / 2.0 + row * pitch
        for column in range(columns):
            center_x = side_margin + pocket_diameter / 2.0 + column * pitch
            straight_pocket = Pos(center_x, center_y, floor_thickness) * Cylinder(
                pocket_diameter / 2.0,
                straight_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            mouth_lead_in = Pos(
                center_x,
                center_y,
                floor_thickness + straight_depth,
            ) * Cone(
                pocket_diameter / 2.0,
                pocket_diameter / 2.0 + lead_in,
                lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - straight_pocket - mouth_lead_in

    return body
