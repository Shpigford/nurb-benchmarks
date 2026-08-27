from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block that holds driver bits upright in two rows of round pockets.

    shank_diameter: how wide the bit shanks are, measured straight across
    columns: how many pockets in each of the two rows
    """
    rows = 2
    clearance = 0.3      # extra on the pocket so a bit drops in and stands
    wall = 2.0           # material between pockets and out to the sides
    pocket_depth = 12.0
    floor = 3.0
    lead_in = 0.8        # chamfer on every pocket mouth and the top perimeter

    pocket_dia = shank_diameter + clearance
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter:g} gives a {pocket_dia:.1f}mm pocket, "
            "under the 2mm minimum printable hole: raise it to 1.7 or more",
            param="shank_diameter",
        )
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pitch = pocket_dia + wall
    width = (columns - 1) * pitch + pocket_dia + 2 * wall
    depth = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = floor + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)
    pockets = [
        Pos(
            (i - (columns - 1) / 2) * pitch,
            (j - (rows - 1) / 2) * pitch,
            floor + (pocket_depth + 1) / 2,
        )
        * Cylinder(pocket_dia / 2, pocket_depth + 1)
        for i in range(columns)
        for j in range(rows)
    ]
    body = body - pockets

    if draft:
        return body
    # Every edge to break lies in the top plane: 4 perimeter edges plus the
    # pocket mouths. The bottom perimeter stays sharp so the footprint is exact.
    top = body.edges().group_by(Axis.Z)[-1]
    return chamfer(top, lead_in)
