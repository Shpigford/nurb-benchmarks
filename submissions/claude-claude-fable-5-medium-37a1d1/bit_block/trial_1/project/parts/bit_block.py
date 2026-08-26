from nurb import *
import math


@part
def bit_block(shank_diameter=6.0, columns=5, rows=2, draft=False):
    """Bench block that holds driver bits upright in round pockets.

    shank_diameter: measured width of a bit shank; each pocket is this plus 0.3 clearance
    columns: how many pockets across the block
    rows: how many pockets front to back
    """
    if shank_diameter < 2.0:
        reject("shank_diameter under 2mm prints as a smear: raise it", param="shank_diameter")
    if columns < 1 or rows < 1:
        reject("the block needs at least one pocket", param="columns")

    clearance = 0.3
    wall = 2.0            # material between pockets and out to the sides
    floor = 3.0           # solid under the pockets
    pocket_depth = 12.0
    chamfer_size = 0.8

    pocket_dia = shank_diameter + clearance
    pitch = pocket_dia + wall
    width = columns * pitch + wall
    depth = rows * pitch + wall
    height = floor + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    x0 = -width / 2 + wall + pocket_dia / 2
    y0 = -depth / 2 + wall + pocket_dia / 2
    pockets = None
    for i in range(columns):
        for j in range(rows):
            p = Pos(x0 + i * pitch, y0 + j * pitch, floor + pocket_depth / 2) * Cylinder(
                pocket_dia / 2, pocket_depth
            )
            pockets = p if pockets is None else pockets + p
    body = body - pockets

    if draft:
        return body

    # Exact 0.8 x 45 lead-in on every pocket mouth and on the top outer perimeter;
    # the bottom perimeter and vertical corners stay sharp.
    top = body.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - height) < 1e-6
                                 and abs(e.bounding_box().max.Z - height) < 1e-6)
    return chamfer(top, chamfer_size)
