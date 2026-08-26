from nurb import *

CLEARANCE = 0.3
WALL = 2.0
POCKET_DEPTH = 12.0
FLOOR = 3.0
LEAD_IN = 0.8
ROWS = 2


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """Holds hex driver bits upright in a grid of round pockets.

    shank_diameter: bit shank across, in mm; pockets are this plus 0.3 clearance
    columns: number of pockets along the long side (two rows)
    """
    if columns < 1:
        reject("need at least one column of pockets", param="columns")
    if shank_diameter <= 0:
        reject("shank diameter must be positive", param="shank_diameter")

    pocket_dia = shank_diameter + CLEARANCE
    if LEAD_IN * 2 >= pocket_dia:
        reject(
            f"0.8 chamfer needs a pocket wider than 1.6; shank_diameter {shank_diameter} is too small",
            param="shank_diameter",
        )

    pitch = pocket_dia + WALL
    length = columns * pitch + WALL
    width = ROWS * pitch + WALL
    height = POCKET_DEPTH + FLOOR
    radius = pocket_dia / 2

    body = Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    x0 = -length / 2 + WALL + radius
    y0 = -width / 2 + WALL + radius
    pockets = []
    for col in range(columns):
        for row in range(ROWS):
            pockets.append(
                Cylinder(radius, POCKET_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
                    Location((x0 + col * pitch, y0 + row * pitch, FLOOR))
                )
            )
    body -= pockets

    if draft:
        return body

    top = body.faces().sort_by(Axis.Z)[-1]
    return chamfer(top.edges(), LEAD_IN)
