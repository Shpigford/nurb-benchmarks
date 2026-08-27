from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block that holds driver bits upright in two rows of round pockets.

    shank_diameter: how wide a bit's shank measures across
    columns: how many pockets long the block is (always two rows deep)
    """
    if columns < 1:
        reject("columns 0 leaves no pockets to hold a bit: use at least 1",
               param="columns")

    pocket_diameter = shank_diameter + 0.3  # drop-in fit over the measured shank
    if pocket_diameter < 2.0:
        reject(f"a {pocket_diameter:.2f}mm pocket is under the 2mm minimum printable "
               "bore: raise shank_diameter above 1.7", param="shank_diameter")

    rows = 2
    pocket_depth = 12.0
    floor = 3.0
    wall = 2.0  # between neighbouring pockets and out to every side
    lead_in = 0.8

    pitch = pocket_diameter + wall
    length = (columns - 1) * pitch + pocket_diameter + 2 * wall
    width = (rows - 1) * pitch + pocket_diameter + 2 * wall
    height = pocket_depth + floor

    block = Pos(0, 0, height / 2) * Box(length, width, height)
    pockets = [
        Pos((c - (columns - 1) / 2) * pitch,
            (r - (rows - 1) / 2) * pitch,
            floor + (pocket_depth + 1.0) / 2)
        * Cylinder(pocket_diameter / 2, pocket_depth + 1.0)
        for c in range(columns)
        for r in range(rows)
    ]
    body = block - pockets

    if draft:
        return body

    # Every pocket mouth must carry the lead-in, so a silent partial polish would
    # be a wrong part; a bare chamfer fails loudly instead. The set is every edge
    # in the top plane: the mouth rims plus the outer perimeter, nothing else.
    top = body.edges().filter_by(lambda e: e.bounding_box().min.Z > height - 1e-6)
    return chamfer(top, lead_in)
