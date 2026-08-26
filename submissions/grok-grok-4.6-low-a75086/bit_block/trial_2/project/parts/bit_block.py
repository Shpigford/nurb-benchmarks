from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank, in mm
    columns: number of pockets across the long side
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter < 2.0:
        reject("shank_diameter is under 2mm; a printed pocket that small closes", param="shank_diameter")

    clearance = 0.3
    pocket_dia = shank_diameter + clearance
    pocket_depth = 12.0
    floor = 3.0
    wall = 2.0
    lead_in = 0.8
    rows = 2
    pitch = pocket_dia + wall
    height = pocket_depth + floor

    width = (columns - 1) * pitch + pocket_dia + 2 * wall
    depth = (rows - 1) * pitch + pocket_dia + 2 * wall

    body = Box(width, depth, height)

    x0 = -width / 2 + wall + pocket_dia / 2
    y0 = -depth / 2 + wall + pocket_dia / 2
    top_z = height / 2
    # Cylinder is centered on Z. Seat it so the floor is exactly pocket_depth
    # below the top, and the cutter only pokes a hair past the mouth.
    overshoot = 0.2
    cutter_h = pocket_depth + overshoot
    cutter_z = top_z + overshoot / 2 - pocket_depth / 2
    for i in range(columns):
        for j in range(rows):
            x = x0 + i * pitch
            y = y0 + j * pitch
            cutter = Cylinder(pocket_dia / 2, cutter_h).move(
                Location((x, y, cutter_z))
            )
            body = body - cutter

    if draft:
        return body

    top = body.faces().sort_by(Axis.Z)[-1]
    outer = top.edges().filter_by(GeomType.LINE)
    mouths = top.edges().filter_by(GeomType.CIRCLE)
    return chamfer(outer + mouths, lead_in)
