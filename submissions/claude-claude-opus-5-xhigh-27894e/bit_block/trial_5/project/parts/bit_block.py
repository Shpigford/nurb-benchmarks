from nurb import *


@part
def bit_block(
    shank_diameter=6.0,
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

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets across the long side
    rows: how many pockets across the short side
    pocket_clearance: how much wider than a shank each pocket is cut
    pocket_depth: how far a bit drops into its pocket
    floor_thickness: how much solid material sits under the pockets
    wall: material between neighbouring pockets, and from a pocket to the block's side
    chamfer_size: the lead-in bevel at each pocket mouth and around the top edge
    """
    if columns < 1 or rows < 1:
        reject(
            "columns and rows are how many pockets the grid holds, so both need at least 1",
            param="columns" if columns < 1 else "rows",
        )

    pocket_diameter = shank_diameter + pocket_clearance
    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket prints as a smear: raise shank_diameter "
            f"above {2.0 - pocket_clearance:.2f}",
            param="shank_diameter",
        )
    # Two chamfered mouths need more than twice the chamfer of flat top between them.
    if wall <= 2 * chamfer_size:
        reject(
            f"a {wall:.2f}mm wall cannot carry a {chamfer_size:.2f}mm chamfer on both "
            f"sides: raise wall above {2 * chamfer_size:.2f}",
            param="wall",
        )

    pitch = pocket_diameter + wall
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Pockets open straight up and stop on a flat floor. They run proud of the top face
    # so the cut never has to resolve two coplanar faces.
    bore = Cylinder(
        pocket_diameter / 2,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for col in range(columns):
        x = (col - (columns - 1) / 2) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, floor_thickness) * bore

    if draft:
        return body

    # Everything lying in the top plane: the outer perimeter and the ten pocket mouths.
    # Nothing else is broken, so the bottom perimeter stays sharp and the bounding box
    # is the block's stated size.
    top = height
    lip = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 1e-6
        and abs(e.bounding_box().max.Z - top) < 1e-6
    )
    return chamfer(lip, chamfer_size)
