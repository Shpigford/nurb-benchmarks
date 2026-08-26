from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank
    columns: how many pockets across the long side
    """
    clearance = 0.3
    pocket_dia = shank_diameter + clearance
    pocket_depth = 12.0
    wall = 2.0
    floor = 3.0
    lead_in = 0.8
    rows = 2

    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", param="shank_diameter")
    if pocket_dia <= 2 * lead_in:
        reject(
            f"shank_diameter {shank_diameter} is too small for the 0.8 lead-in",
            param="shank_diameter",
        )

    pitch = pocket_dia + wall
    length = (columns - 1) * pitch + pocket_dia + 2 * wall
    width = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = pocket_depth + floor

    body = Box(length, width, height)

    x0 = -length / 2 + wall + pocket_dia / 2
    y0 = -width / 2 + wall + pocket_dia / 2
    pocket_z = height / 2 - pocket_depth

    cut = None
    for i in range(columns):
        for j in range(rows):
            cyl = Cylinder(
                pocket_dia / 2,
                pocket_depth + 0.02,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            cyl = cyl.move(Location((x0 + i * pitch, y0 + j * pitch, pocket_z)))
            cut = cyl if cut is None else cut + cyl
    body = body - cut

    if draft:
        return body

    top_z = body.bounding_box().max.Z
    top_edges = body.edges().filter_by(
        lambda e: abs(e.bounding_box().max.Z - top_z) < 1e-4
        and abs(e.bounding_box().min.Z - top_z) < 1e-4
    )
    return chamfer(top_edges, lead_in)
