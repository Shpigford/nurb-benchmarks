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
    """A bench block that stands driver bits upright in a grid of round pockets.

    shank_diameter: measured width across a bit shank, what the pockets are sized from
    columns: how many pockets across the long side
    rows: how many pockets across the short side
    pocket_clearance: extra width so a bit drops in rather than press-fits
    pocket_depth: how far a bit sinks into the block
    floor_thickness: solid material under the pockets
    wall: material between neighbouring pockets and out to the block's sides
    chamfer_size: the lead-in broken around each pocket mouth and the top perimeter
    """
    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia < 2.0:
        reject(
            f"a {pocket_dia:.1f}mm pocket prints as a smear; "
            "raise shank_diameter above 1.7",
            param="shank_diameter",
        )
    if columns < 1 or rows < 1:
        reject("a block needs at least one pocket", param="columns")
    # Two chamfered mouths need more than 2 * chamfer_size of face between them
    # (kernel rule), and the doctrine's wall floor is stricter still.
    if wall < 2 * chamfer_size:
        reject(
            f"{wall}mm between pockets is under the {2 * chamfer_size}mm two "
            "chamfers need to land; raise wall",
            param="wall",
        )

    pitch = pocket_dia + wall
    width = (columns - 1) * pitch + pocket_dia + 2 * wall
    depth = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = floor_thickness + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    # Pockets open straight up, flat floors at floor_thickness, and run past the
    # top face so the mouth resolves as one clean circle to chamfer.
    bore = Cylinder(
        pocket_dia / 2,
        pocket_depth + chamfer_size,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for i in range(columns):
        for j in range(rows):
            x = (i - (columns - 1) / 2) * pitch
            y = (j - (rows - 1) / 2) * pitch
            body -= Pos(x, y, floor_thickness) * bore

    if draft:
        return body

    # Only the top: every pocket mouth gets its lead-in and the top perimeter
    # matches it. The bottom perimeter and the vertical corners stay sharp, so
    # the block's stated footprint is the footprint.
    top = body.bounding_box().max.Z
    mouths = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6
    )
    return polish(body, mouths, chamfer_size)
