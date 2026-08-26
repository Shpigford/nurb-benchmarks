from nurb import *

@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank
    columns: number of pockets across the long side
    """
    rows = 2
    clearance = 0.3
    pocket_diameter = shank_diameter + clearance
    pocket_depth = 12.0
    floor_thickness = 3.0
    wall = 2.0
    lead_in = 0.8
    pitch = pocket_diameter + wall
    height = floor_thickness + pocket_depth
    length = columns * pocket_diameter + (columns - 1) * wall + 2 * wall
    width = rows * pocket_diameter + (rows - 1) * wall + 2 * wall

    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    block = Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    first_x = -length / 2 + wall + pocket_diameter / 2
    first_y = -width / 2 + wall + pocket_diameter / 2
    pockets = []
    for col in range(columns):
        for row in range(rows):
            x = first_x + col * pitch
            y = first_y + row * pitch
            pockets.append(
                Pos(x, y, floor_thickness)
                * Cylinder(pocket_diameter / 2, pocket_depth + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
            )
    body = block - pockets

    if draft:
        return body

    top_z = body.bounding_box().max.Z
    mouths_and_rim = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top_z) < 1e-4
        and abs(e.bounding_box().max.Z - top_z) < 1e-4
    )
    return chamfer(mouths_and_rim, lead_in)
