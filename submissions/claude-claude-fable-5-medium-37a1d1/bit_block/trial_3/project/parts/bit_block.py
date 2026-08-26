from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall_between_pockets=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """Bench block that holds driver bits standing upright in round pockets.

    shank_diameter: measured width of a bit's shank, what the pockets are sized from
    columns: how many pockets along the block's length
    rows: how many pockets across the block's width
    pocket_clearance: extra pocket width over the shank so a bit drops in freely
    pocket_depth: how deep each bit sinks into the block
    wall_between_pockets: material between neighbouring pockets and out to the sides
    floor_thickness: solid material under the pocket floors
    chamfer_size: lead-in chamfer at each pocket mouth and on the top outer edge
    """
    if columns < 1 or rows < 1:
        reject("the block needs at least one pocket", param="columns")
    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia < 2.0:
        reject("pockets under 2mm will not print open: raise shank_diameter", param="shank_diameter")
    pitch = pocket_dia + wall_between_pockets
    length = columns * pitch + wall_between_pockets
    width = rows * pitch + wall_between_pockets
    height = floor_thickness + pocket_depth

    block = Pos(length / 2, width / 2, height / 2) * Box(length, width, height)
    x0 = wall_between_pockets + pocket_dia / 2
    y0 = wall_between_pockets + pocket_dia / 2
    pockets = [
        Pos(x0 + i * pitch, y0 + j * pitch, floor_thickness + pocket_depth / 2)
        * Cylinder(pocket_dia / 2, pocket_depth)
        for i in range(columns)
        for j in range(rows)
    ]
    for p in pockets:
        block = block - p
    if draft:
        return block

    # Every edge in the top face: the outer perimeter and each pocket mouth.
    top = block.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - height) < 1e-6
                                  and abs(e.bounding_box().max.Z - height) < 1e-6)
    return chamfer(top, chamfer_size)
