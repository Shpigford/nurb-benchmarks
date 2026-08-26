from nurb import *

ROWS = 2
CLEARANCE = 0.3
POCKET_DEPTH = 12.0
WALL = 2.0
FLOOR = 3.0
LEAD_IN = 0.8


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured bit shank across (pockets are this plus 0.3)
    columns: number of pockets across the long side
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pocket_dia = shank_diameter + CLEARANCE
    pitch = pocket_dia + WALL
    width = (columns + 1) * WALL + columns * pocket_dia
    depth = (ROWS + 1) * WALL + ROWS * pocket_dia
    height = POCKET_DEPTH + FLOOR

    body = Box(width, depth, height)
    origin_x = -width / 2
    origin_y = -depth / 2
    first_x = origin_x + WALL + pocket_dia / 2
    first_y = origin_y + WALL + pocket_dia / 2
    cutter_h = POCKET_DEPTH + 2.0
    cutter_z = -height / 2 + FLOOR + cutter_h / 2

    for col in range(columns):
        for row in range(ROWS):
            x = first_x + col * pitch
            y = first_y + row * pitch
            body -= Cylinder(pocket_dia / 2, cutter_h).locate(Location((x, y, cutter_z)))

    if draft:
        return body

    top_z = body.bounding_box().max.Z
    mouths = body.edges().filter_by(GeomType.CIRCLE).filter_by(
        lambda e: abs(e.center().Z - top_z) < 0.05
    )
    outer_top = body.edges().filter_by(GeomType.LINE).filter_by(
        lambda e: abs(e.bounding_box().min.Z - top_z) < 0.05
        and abs(e.bounding_box().max.Z - top_z) < 0.05
    )
    return chamfer(mouths + outer_top, LEAD_IN)
