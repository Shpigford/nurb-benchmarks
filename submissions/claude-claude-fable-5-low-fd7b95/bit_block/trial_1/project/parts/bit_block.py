from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5, draft=False):
    """A bench block that holds driver bits upright in round pockets.

    shank_diameter: how wide the bit shafts are, measured across
    columns: how many pockets across the block
    """
    if shank_diameter < 1.7:
        reject(
            "shank_diameter %.2f leaves pockets under the 2mm printable hole "
            "floor: raise it above 1.7" % shank_diameter,
            param="shank_diameter",
        )
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    wall = 2.0
    rows = 2
    pocket_diameter = shank_diameter + 0.3
    pocket_depth = 12.0
    floor = 3.0
    cham = 0.8

    pitch = pocket_diameter + wall
    width = columns * pitch + wall
    depth = rows * pitch + wall
    height = pocket_depth + floor

    block = Pos(0, 0, height / 2) * Box(width, depth, height)

    if not draft:
        top = block.edges().filter_by(
            lambda e: e.bounding_box().min.Z > height - 1e-6
        )
        block = chamfer(top, cham)

    r = pocket_diameter / 2
    cutters = []
    for i in range(columns):
        for j in range(rows):
            x = (i - (columns - 1) / 2) * pitch
            y = (j - (rows - 1) / 2) * pitch
            cutters.append(
                Pos(x, y, height - pocket_depth / 2) * Cylinder(r, pocket_depth)
            )
            # Lead-in cut as a cone so neighbouring mouths, only 0.4mm apart
            # after chamfering, never meet in one chamfer op. Extended 0.5
            # above the top face at the same 45 degrees, so the mouth still
            # opens to exactly r + cham at the surface.
            lead = cham + 0.5
            cutters.append(
                Pos(x, y, height - cham + lead / 2) * Cone(r, r + lead, lead)
            )

    return block - cutters
