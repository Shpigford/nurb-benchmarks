from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block that holds driver bits upright, shanks in round pockets.

    shank_diameter: how wide a bit's shank is, straight across
    columns: how many pockets in each of the two rows
    """
    rows = 2
    wall = 2.0          # material between pocket walls, and out to the sides
    clearance = 0.3     # extra across each pocket so a bit drops in and stands
    pocket_depth = 12.0
    floor = 3.0
    lead_in = 0.8       # chamfer on the pocket mouths and the top perimeter

    if columns < 1:
        reject("columns must be at least 1", param="columns")
    pocket_dia = shank_diameter + clearance
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} makes a {pocket_dia:.1f}mm pocket, "
            "under the 2mm a printed hole needs: raise it above 1.7",
            param="shank_diameter",
        )

    pitch = pocket_dia + wall
    length = (columns - 1) * pitch + pocket_dia + 2 * wall
    width = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = floor + pocket_depth

    body = Pos(0, 0, height / 2) * Box(length, width, height)
    x0 = -(columns - 1) * pitch / 2
    y0 = -(rows - 1) * pitch / 2
    pockets = [
        Pos(x0 + i * pitch, y0 + j * pitch, height - pocket_depth / 2)
        * Cylinder(pocket_dia / 2, pocket_depth)
        for i in range(columns)
        for j in range(rows)
    ]
    body = body - pockets

    if draft:
        return body

    # Break only the edges lying in the top plane: the four perimeter edges and
    # every pocket mouth. The bottom perimeter and the vertical corners stay
    # sharp so the bounding box is exactly what the numbers say.
    top_edges = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > height - 1e-4
    )
    return polish(body, top_edges, lead_in)
