from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5, rows=2, draft=False):
    """A bench block that holds driver bits upright in round pockets.

    shank_diameter: how wide the bit shanks are, measured across
    columns: how many pockets across the long side
    rows: how many pockets front to back
    """
    clearance = 0.3
    wall = 2.0
    pocket_dia = shank_diameter + clearance
    pocket_depth = 12.0
    floor = 3.0
    chamfer_size = 0.8

    pitch = pocket_dia + wall
    length = (columns - 1) * pitch + pocket_dia + 2 * wall
    width = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = floor + pocket_depth

    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} makes a {pocket_dia:.1f}mm pocket, "
            "under the 2mm printable-hole floor: raise it above 1.7",
            param="shank_diameter",
        )

    body = Pos(length / 2, width / 2, height / 2) * Box(length, width, height)
    for c in range(columns):
        for r in range(rows):
            cx = wall + pocket_dia / 2 + c * pitch
            cy = wall + pocket_dia / 2 + r * pitch
            body -= Pos(cx, cy, height - pocket_depth / 2) * Cylinder(
                pocket_dia / 2, pocket_depth
            )

    if draft:
        return body

    # Only the top-face edges get the 0.8 lead-in: pocket mouths and the outer
    # perimeter. Everything else, the bottom perimeter included, stays sharp so
    # the stated bounding box is exact.
    top = body.edges().filter_by(lambda e: e.bounding_box().min.Z > height - 0.01)
    return polish(body, top, chamfer_size)
