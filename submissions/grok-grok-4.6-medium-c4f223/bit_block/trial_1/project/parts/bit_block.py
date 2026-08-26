from nurb import *

# Fit and structure. Pocket diameter is shank plus print clearance; pitch keeps
# 2mm of wall between neighbouring pockets and the same 2mm from the outermost
# pocket walls to the block sides.
_CLEARANCE = 0.3
_POCKET_DEPTH = 12.0
_FLOOR = 3.0
_WALL = 2.0
_LEAD = 0.8
_ROWS = 2


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: bit shank across, in mm
    columns: how many pockets across the front of the block
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pocket_dia = shank_diameter + _CLEARANCE
    if pocket_dia <= 2 * _LEAD:
        reject(
            f"shank_diameter {shank_diameter} leaves a {pocket_dia:.1f}mm pocket, "
            f"too small for the {_LEAD}mm mouth chamfer: raise it above "
            f"{2 * _LEAD - _CLEARANCE}",
            param="shank_diameter",
        )

    pocket_r = pocket_dia / 2
    pitch = pocket_dia + _WALL
    width = columns * pocket_dia + (columns + 1) * _WALL
    depth = _ROWS * pocket_dia + (_ROWS + 1) * _WALL
    height = _POCKET_DEPTH + _FLOOR

    # Outer top chamfer is a 0.8 x 45 frustum lofted onto the block, not an
    # edge chamfer: chamfering the four top edges would leave a sub-1mm triangle
    # at each corner.
    base = Box(width, depth, height - _LEAD, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lower = Plane.XY.offset(height - _LEAD) * Rectangle(width, depth)
    upper = Plane.XY.offset(height) * Rectangle(width - 2 * _LEAD, depth - 2 * _LEAD)
    body = base + loft([lower, upper])

    x0 = -width / 2 + _WALL + pocket_r
    y0 = -depth / 2 + _WALL + pocket_r
    for col in range(columns):
        for row in range(_ROWS):
            pin = Cylinder(
                pocket_r,
                _POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - Location((x0 + col * pitch, y0 + row * pitch, _FLOOR)) * pin

    mouths = [
        edge
        for edge in body.edges()
        if edge.geom_type == GeomType.CIRCLE and abs(edge.center().Z - height) < 1e-3
    ]
    return chamfer(mouths, _LEAD)
