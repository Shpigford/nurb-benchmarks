from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank
    columns: how many pockets across the block
    """
    clearance = 0.3
    wall = 2.0
    floor = 3.0
    pocket_depth = 12.0
    lead_in = 0.8
    rows = 2

    if columns < 1:
        reject("columns must be at least 1 so there is a pocket to stand a bit in", param="columns")

    pocket_dia = shank_diameter + clearance
    if pocket_dia < 2.0:
        reject(
            f"pocket diameter {pocket_dia:.1f} is under 2mm: raise shank_diameter above {2.0 - clearance}",
            param="shank_diameter",
        )

    pocket_r = pocket_dia / 2.0
    pitch = pocket_dia + wall
    length = columns * pitch + wall
    width = rows * pitch + wall
    height = pocket_depth + floor

    body = Box(length, width, height, align=(Align.MIN, Align.MIN, Align.MIN))

    for i in range(columns):
        for j in range(rows):
            x = wall + pocket_r + i * pitch
            y = wall + pocket_r + j * pitch
            cutter = Pos(x, y, floor) * Cylinder(
                pocket_r,
                pocket_depth + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body -= cutter

    if draft:
        return body

    top = body.faces().sort_by(Axis.Z)[-1]
    return chamfer(top.edges(), lead_in)
