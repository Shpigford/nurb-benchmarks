from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    shank_clearance=0.3,
    pocket_depth=12.0,
    floor_thickness=3.0,
    wall_thickness=2.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run along the long side of the block
    rows: how many pockets run across the short side of the block
    shank_clearance: extra width in each pocket so a bit drops straight in
    pocket_depth: how deep a bit sinks into the block
    floor_thickness: solid material left under the pockets
    wall_thickness: material between neighbouring pockets, and out to the sides
    chamfer_size: the lead-in broken off each pocket mouth and the top rim
    """
    if columns < 1 or rows < 1:
        reject("a block needs at least one pocket", param="columns")
    pocket_diameter = shank_diameter + shank_clearance
    if pocket_diameter < 2.0:
        reject(
            f"shank_diameter {shank_diameter} leaves a {pocket_diameter:.2f}mm bore, "
            "under the 2mm a printed hole survives: raise it above "
            f"{2.0 - shank_clearance:.2f}",
            param="shank_diameter",
        )
    if chamfer_size < 0.8:
        reject(
            f"chamfer_size {chamfer_size} is under the 0.8mm floor a chamfer prints at: "
            "raise it to 0.8 or more",
            param="chamfer_size",
        )
    # Two chamfered mouths share the wall between them, and OCCT needs more than
    # 2 * chamfer_size of flat face left over or the whole pass falls over.
    if wall_thickness <= 2 * chamfer_size:
        reject(
            f"wall_thickness {wall_thickness} leaves no flat between two "
            f"{chamfer_size}mm mouth chamfers: raise it above {2 * chamfer_size:.2f}",
            param="wall_thickness",
        )

    # One pitch is a pocket plus the wall to its neighbour, and the same wall runs
    # from the outermost pockets out to the sides, so the block is exactly the grid
    # plus a border.
    pitch = pocket_diameter + wall_thickness
    block_width = (columns - 1) * pitch + pocket_diameter + 2 * wall_thickness
    block_depth = (rows - 1) * pitch + pocket_diameter + 2 * wall_thickness
    height = pocket_depth + floor_thickness

    body = Pos(0, 0, height / 2) * Box(block_width, block_depth, height)

    pocket = Cylinder(pocket_diameter / 2, pocket_depth)
    for column in range(columns):
        x = (column - (columns - 1) / 2) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, height - pocket_depth / 2) * pocket

    if draft:
        return body
    # Only the edges lying in the top face: the ten pocket mouths and the outer rim.
    # The bottom perimeter and the vertical corners stay sharp so the block's stated
    # footprint is what sits on the bench.
    top = body.bounding_box().max.Z
    rim = body.edges().filter_by(lambda e: e.bounding_box().min.Z > top - 1e-6)
    return polish(body, rim, chamfer_size)
