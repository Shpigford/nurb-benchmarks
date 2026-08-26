from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5, draft=False):
    """A bench block that holds driver bits upright in round pockets.

    shank_diameter: how wide the bit shanks are, measured across
    columns: how many pockets in each row
    """
    rows = 2
    clearance = 0.3
    wall = 2.0
    pocket_dia = shank_diameter + clearance
    pocket_depth = 12.0
    floor = 3.0
    cham = 0.8

    pitch = pocket_dia + wall
    width = columns * pitch + wall
    depth = rows * pitch + wall
    height = floor + pocket_depth

    if pocket_dia < 2.0:
        reject(
            "shank_diameter %.2f leaves a pocket under the 2mm printable "
            "minimum: raise it above 1.7" % shank_diameter,
            param="shank_diameter",
        )
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    body = Box(width, depth, height)
    top = body.bounding_box().max.Z

    pockets = []
    x0 = -(columns - 1) * pitch / 2
    y0 = -(rows - 1) * pitch / 2
    for c in range(columns):
        for r in range(rows):
            pockets.append(
                Pos(x0 + c * pitch, y0 + r * pitch, top - pocket_depth / 2)
                * Cylinder(pocket_dia / 2, pocket_depth)
            )
    body = body - pockets

    if draft:
        return body
    # Lead-in on every pocket mouth and the top outer perimeter, nothing else:
    # the bottom perimeter and vertical corners stay sharp so the box is exact.
    top_edges = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6
    )
    return polish(body, top_edges, cham)
