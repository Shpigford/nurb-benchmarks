from nurb import *

_CLEARANCE = 0.3
_POCKET_DEPTH = 12.0
_FLOOR = 3.0
_WALL = 2.0
_LEAD = 0.8
_ROWS = 2


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank; pockets are this plus 0.3 of clearance
    columns: number of pockets in each row
    """
    if columns < 1:
        reject("columns must be at least 1 so there is a pocket to stand a bit in", param="columns")
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")

    pocket_dia = shank_diameter + _CLEARANCE
    if pocket_dia <= 2 * _LEAD:
        reject(
            f"shank_diameter {shank_diameter} leaves a {pocket_dia}mm pocket, too small "
            f"for the {_LEAD}mm mouth chamfer: raise it above {2 * _LEAD - _CLEARANCE}",
            param="shank_diameter",
        )

    pitch = pocket_dia + _WALL
    height = _FLOOR + _POCKET_DEPTH
    length = columns * pitch + _WALL
    width = _ROWS * pitch + _WALL

    body = Box(length, width, height, align=(Align.MIN, Align.MIN, Align.MIN))

    pockets = []
    for col in range(columns):
        for row in range(_ROWS):
            x = _WALL + pocket_dia / 2 + col * pitch
            y = _WALL + pocket_dia / 2 + row * pitch
            cutter = Cylinder(
                pocket_dia / 2,
                _POCKET_DEPTH + 0.2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            pockets.append(Pos(x, y, _FLOOR) * cutter)
    body = body - pockets[0]
    for p in pockets[1:]:
        body = body - p

    if draft:
        return body

    top = body.faces().sort_by(Axis.Z)[-1]
    return chamfer(top.edges(), _LEAD)
