from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    floor_thickness=3.0,
    wall=2.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets across the long side
    rows: how many pockets across the short side
    pocket_clearance: extra width in a pocket so a shank drops in
    pocket_depth: how deep a bit sinks into the block
    floor_thickness: solid material under the pockets
    wall: material between neighbouring pockets and out to the sides
    chamfer_size: the lead-in break at every pocket mouth and the top rim
    """
    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} makes a {pocket_dia:.1f}mm pocket, "
            "under the 2mm bore floor: raise it above 1.7",
            param="shank_diameter",
        )
    if wall <= 2 * chamfer_size:
        reject(
            f"wall {wall} leaves no face between neighbouring {chamfer_size}mm "
            f"chamfers: raise it above {2 * chamfer_size}",
            param="wall",
        )

    pitch = pocket_dia + wall
    width = columns * pocket_dia + (columns + 1) * wall
    depth = rows * pocket_dia + (rows + 1) * wall
    height = pocket_depth + floor_thickness

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    for col in range(columns):
        x = (col - (columns - 1) / 2) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, height - pocket_depth / 2) * Cylinder(
                pocket_dia / 2, pocket_depth
            )

    if draft:
        return body

    top = body.bounding_box().max.Z
    rim = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6
    )
    return polish(body, rim, chamfer_size)
