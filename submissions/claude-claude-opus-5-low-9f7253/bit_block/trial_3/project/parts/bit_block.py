from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    floor_thickness=3.0,
    wall_thickness=2.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets across the long side
    rows: how many pockets across the short side
    pocket_clearance: extra width in a pocket so a bit drops in freely
    pocket_depth: how deep a bit sinks into the block
    floor_thickness: solid material under the pockets
    wall_thickness: material between neighbouring pockets and out to the sides
    chamfer_size: the lead-in break at each pocket mouth and the top edges
    """
    pocket_diameter = shank_diameter + pocket_clearance
    if pocket_diameter < 2.0:
        reject("a pocket under 2mm across prints closed", "shank_diameter")
    if columns < 1 or rows < 1:
        reject("the grid needs at least one pocket", "columns")

    pitch = pocket_diameter + wall_thickness
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall_thickness
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall_thickness
    height = pocket_depth + floor_thickness

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    for i in range(columns):
        x = (i - (columns - 1) / 2) * pitch
        for j in range(rows):
            y = (j - (rows - 1) / 2) * pitch
            cut = Pos(x, y, height - pocket_depth / 2) * Cylinder(
                pocket_diameter / 2, pocket_depth
            )
            body = body - cut

    if draft:
        return body

    top = body.bounding_box().max.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6
    )
    return polish(body, keep, chamfer_size)
