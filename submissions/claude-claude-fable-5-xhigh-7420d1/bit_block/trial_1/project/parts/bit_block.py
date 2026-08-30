from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall=2.0,
    floor=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: how wide a bit shank is, measured across it
    columns: how many pockets along the block
    rows: how many pockets across the block
    pocket_clearance: how much wider each pocket is than the shank
    pocket_depth: how far a bit sinks into its pocket
    wall: material between neighbouring pockets, and from the outer pockets to the sides
    floor: solid material under the pocket floors
    chamfer_size: the lead-in on every pocket mouth, and the bevel on the top outer edge
    """
    pocket_diameter = shank_diameter + pocket_clearance
    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket prints closed: raise shank_diameter",
            param="shank_diameter",
        )
    if columns < 1:
        reject("the block needs at least one column of pockets", param="columns")
    if rows < 1:
        reject("the block needs at least one row of pockets", param="rows")
    if wall <= 2 * chamfer_size:
        reject(
            f"wall {wall} leaves no room for two {chamfer_size}mm chamfers to meet: "
            f"raise it above {2 * chamfer_size}",
            param="wall",
        )

    pitch = pocket_diameter + wall
    length = columns * pitch + wall
    width = rows * pitch + wall
    height = floor + pocket_depth

    body = Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pockets = [
        Pos(loc.position.X, loc.position.Y, floor)
        * Cylinder(
            pocket_diameter / 2,
            pocket_depth + 1.0,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for loc in GridLocations(pitch, pitch, columns, rows)
    ]
    body = body - pockets
    if draft:
        return body

    # Only the top face's edges get broken: the outer perimeter and every pocket
    # mouth. The bottom perimeter and the vertical corners stay sharp so the
    # footprint is exactly what the numbers say.
    top = body.edges().group_by(Axis.Z)[-1]
    return chamfer(top, chamfer_size)
