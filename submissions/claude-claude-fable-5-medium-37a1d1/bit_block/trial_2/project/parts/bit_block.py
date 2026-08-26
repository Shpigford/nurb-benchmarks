from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5, rows=2, draft=False):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: width of the bit shank, in mm (pockets are 0.3 larger)
    columns: how many pockets across the block
    rows: how many pockets front to back
    """
    if columns < 1:
        reject("need at least one column", param="columns")
    clearance = 0.3
    wall = 2.0
    pocket_depth = 12.0
    floor = 3.0
    lead_in = 0.8
    pocket_dia = shank_diameter + clearance
    pitch = pocket_dia + wall
    width = columns * pitch + wall
    depth = rows * pitch + wall
    height = pocket_depth + floor

    body = Box(width, depth, height, align=(Align.MIN, Align.MIN, Align.MIN))
    pockets = []
    for i in range(columns):
        for j in range(rows):
            x = wall + pocket_dia / 2 + i * pitch
            y = wall + pocket_dia / 2 + j * pitch
            pockets.append(
                Pos(x, y, floor + pocket_depth / 2)
                * Cylinder(pocket_dia / 2, pocket_depth)
            )
    for p in pockets:
        body = body - p
    if draft:
        return body
    top = body.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - height) < 1e-6
                                 and abs(e.bounding_box().max.Z - height) < 1e-6)
    return polish(body, top, lead_in)
