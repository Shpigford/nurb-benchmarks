from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A compact bench block for storing driver bits upright.

    shank_diameter: diameter of the bit shank the pockets must hold
    columns: number of pockets across the block
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1 or int(columns) != columns:
        reject("columns must be a positive whole number", param="columns")

    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    pitch = 8.3
    side_margin = 2.0
    mouth_chamfer = 0.8
    rows = 2

    width = pocket_diameter + 2.0 * side_margin + (columns - 1) * pitch
    depth = pocket_diameter + 2.0 * side_margin + (rows - 1) * pitch
    height = floor_thickness + pocket_depth

    body = Box(
        width,
        depth,
        height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Only the four top perimeter edges are cosmetic polish.  In particular, the
    # bottom perimeter remains sharp so the stated footprint stays exact.
    if not draft:
        top_edges = body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > height - 1e-6
        )
        body = polish(body, top_edges, mouth_chamfer)

    # The cylindrical portion reaches the flat floor 12 mm below the top.  The
    # overlapping frustum adds the exact 0.8 x 45-degree lead-in at each mouth.
    for row in range(rows):
        for column in range(int(columns)):
            x = side_margin + pocket_radius + column * pitch
            y = side_margin + pocket_radius + row * pitch
            pocket = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            lead_in = Pos(x, y, height - mouth_chamfer) * Cone(
                pocket_radius,
                pocket_radius + mouth_chamfer,
                mouth_chamfer,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - pocket - lead_in

    return body
