from nurb import *

CLEARANCE = 0.3
WALL = 2.0
POCKET_DEPTH = 12.0
FLOOR = 3.0
LEAD_IN = 0.8
ROWS = 2


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank
    columns: how many pockets across the block
    """
    if columns < 1:
        reject("columns must be at least 1 so the grid has somewhere to put a bit", param="columns")
    if shank_diameter < 2.0:
        reject(
            f"shank_diameter {shank_diameter} is under 2mm; a printed pocket that small closes up",
            param="shank_diameter",
        )

    pocket_dia = shank_diameter + CLEARANCE
    pocket_r = pocket_dia / 2
    pitch = pocket_dia + WALL
    width = WALL + columns * pitch
    depth = WALL + ROWS * pitch
    height = POCKET_DEPTH + FLOOR

    body = Box(width, depth, height, align=(Align.MIN, Align.MIN, Align.MIN))
    for col in range(columns):
        for row in range(ROWS):
            x = WALL + pocket_r + col * pitch
            y = WALL + pocket_r + row * pitch
            cutter = Cylinder(
                pocket_r,
                POCKET_DEPTH + 1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body -= Pos(x, y, FLOOR) * cutter

    mouths = body.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1]
    body = chamfer(mouths, LEAD_IN)

    top_z = body.bounding_box().max.Z
    top_outer = body.edges().filter_by(GeomType.LINE).filter_by(
        lambda e: abs(e.bounding_box().min.Z - top_z) < 1e-4
        and abs(e.bounding_box().max.Z - top_z) < 1e-4
    )
    return chamfer(top_outer, LEAD_IN)
