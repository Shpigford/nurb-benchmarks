from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run along the long side
    rows: how many pockets run across the short side
    pocket_clearance: how much wider than a shank each pocket is, so bits drop in
    pocket_depth: how deep a bit sinks into the block
    wall: material between neighbouring pockets and out to the block's sides
    floor_thickness: solid material under the pocket floors
    chamfer_size: the lead-in broken around each pocket mouth and the top rim
    """
    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia <= 0:
        reject("shank diameter has to be positive", "shank_diameter")
    if columns < 1 or rows < 1:
        reject("the grid needs at least one pocket", "columns")
    if wall <= 2 * chamfer_size:
        reject(
            f"{wall}mm between pockets cannot carry two {chamfer_size}mm chamfers",
            "wall",
        )

    pitch = pocket_dia + wall
    length = columns * pocket_dia + (columns + 1) * wall
    width = rows * pocket_dia + (rows + 1) * wall
    height = pocket_depth + floor_thickness

    body = Box(length, width, height)
    top = body.bounding_box().max.Z

    centers = [
        (
            (c - (columns - 1) / 2) * pitch,
            (r - (rows - 1) / 2) * pitch,
        )
        for c in range(columns)
        for r in range(rows)
    ]
    for x, y in centers:
        pocket = Cylinder(pocket_dia / 2, pocket_depth).locate(
            Location((x, y, top - pocket_depth / 2))
        )
        body = body - pocket

    if draft:
        return body

    rim = body.edges().filter_by(lambda e: abs(e.bounding_box().min.Z - top) < 1e-6)
    rim = rim.filter_by(lambda e: abs(e.bounding_box().max.Z - top) < 1e-6)
    return polish(body, rim, chamfer_size)
