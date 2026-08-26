from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: bit shank width across
    columns: number of pockets in each row
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")

    clearance = 0.3
    wall = 2.0
    margin = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    rows = 2

    pocket_dia = shank_diameter + clearance
    if pocket_dia <= 2 * lead_in:
        reject(
            f"shank_diameter {shank_diameter} is too small for the {lead_in} mm lead-in",
            param="shank_diameter",
        )

    pocket_r = pocket_dia / 2.0
    pitch = pocket_dia + wall
    width = 2.0 * margin + columns * pocket_dia + (columns - 1) * wall
    depth = 2.0 * margin + rows * pocket_dia + (rows - 1) * wall
    height = pocket_depth + floor_thickness

    body = Box(width, depth, height, align=(Align.MIN, Align.MIN, Align.MIN))

    pockets = []
    for col in range(columns):
        for row in range(rows):
            cx = margin + pocket_r + col * pitch
            cy = margin + pocket_r + row * pitch
            pockets.append(
                Pos(cx, cy, floor_thickness)
                * Cylinder(
                    pocket_r,
                    pocket_depth + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            )
    body = body - pockets

    top_z = body.bounding_box().max.Z
    mouths = body.edges().filter_by(
        lambda e: abs(e.center().Z - top_z) < 1e-4
        and abs(e.bounding_box().size.Z) < 1e-4
    )
    return chamfer(mouths, lead_in)
