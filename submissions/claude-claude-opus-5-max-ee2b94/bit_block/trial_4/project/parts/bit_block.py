from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    pocket_clearance=0.3,
    pocket_depth=12.0,
    columns=5,
    rows=2,
    wall=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that stands driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    pocket_clearance: how much wider than a shank a pocket is, so a bit drops straight in
    pocket_depth: how far a bit sinks into the block
    columns: how many pockets along the long side
    rows: how many pockets along the short side
    wall: material between neighbouring pockets, and from a pocket to the block's side
    floor_thickness: solid material under the pocket floors
    chamfer_size: the lead-in bevel at each pocket mouth, and around the top edge
    """
    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia < 2.0:
        reject(
            f"a {pocket_dia:.2f}mm pocket prints as a smear or closes outright: "
            f"raise shank_diameter above {2.0 - pocket_clearance:.2f}",
            param="shank_diameter",
        )
    if columns < 1 or rows < 1:
        reject("a block with no pockets holds no bits: columns and rows are at least 1")
    # Two chamfered mouths need more than 2 * chamfer_size of face between them, and the
    # same wall carries the block's own top edge chamfer past the outermost pockets.
    if wall <= 2 * chamfer_size:
        reject(
            f"a {wall:.2f}mm wall cannot carry two {chamfer_size:.2f}mm chamfers: "
            f"raise wall above {2 * chamfer_size:.2f}",
            param="wall",
        )

    pitch = pocket_dia + wall
    width = (columns - 1) * pitch + pocket_dia + 2 * wall
    depth = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # The bottom perimeter stays sharp: it is the bed-contact face, and the stated
    # bounding box is measured off it.
    if not draft:
        body = polish(body, body.edges().group_by(Axis.Z)[-1], chamfer_size)

    # A pocket is its own negative: a flat-floored bore with a 45 degree lead-in cut
    # into the mouth, rather than a chamfer selected afterwards. The mouths sit
    # 2 * chamfer_size apart, which is exactly where the kernel starts refusing them.
    bore = Cylinder(
        pocket_dia / 2,
        pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    lead_in = Cone(
        pocket_dia / 2,
        pocket_dia / 2 + chamfer_size,
        chamfer_size,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = bore + Pos(0, 0, pocket_depth - chamfer_size) * lead_in

    for column in range(columns):
        for row in range(rows):
            x = (column - (columns - 1) / 2) * pitch
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, floor_thickness) * pocket

    return body
