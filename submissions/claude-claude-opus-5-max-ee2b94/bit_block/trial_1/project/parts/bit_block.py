from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall_thickness=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that stands driver bits upright in a grid of round pockets.

    shank_diameter: how thick the bit shanks are across
    columns: how many pockets along the long side of the block
    rows: how many pockets along the short side of the block
    pocket_clearance: how much wider a pocket is than a shank, so bits drop straight in
    pocket_depth: how far a bit sinks into the block
    wall_thickness: material between neighbouring pockets, and out to the block's sides
    floor_thickness: solid material under the pockets
    chamfer_size: the lead-in broken around each pocket mouth and the top outer edge
    """
    if columns < 1 or rows < 1:
        reject("the grid needs at least one pocket", param="columns")
    pocket_diameter = shank_diameter + pocket_clearance
    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket is under the 2mm printable bore: "
            f"raise shank_diameter above {2.0 - pocket_clearance:.2f}",
            param="shank_diameter",
        )
    if wall_thickness <= 2 * chamfer_size:
        reject(
            f"a {wall_thickness:.2f}mm wall leaves no face between two {chamfer_size:.2f}mm "
            f"chamfer toes: raise wall_thickness above {2 * chamfer_size:.2f}",
            param="wall_thickness",
        )
    if floor_thickness <= chamfer_size or pocket_depth <= chamfer_size:
        reject(
            "the pocket mouth chamfer has to land inside the pocket wall: "
            f"keep pocket_depth and floor_thickness above {chamfer_size:.2f}",
            param="chamfer_size",
        )

    # One pitch carries a pocket and the wall beside it, so a block that is `columns`
    # pitches wide has exactly one wall left over: half at each end.
    pitch = pocket_diameter + wall_thickness
    width = columns * pitch + wall_thickness
    depth = rows * pitch + wall_thickness
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height)
    top = body.bounding_box().max.Z

    # The bores run past the top face so the only new face the cut makes is the flat
    # floor; a cutter ending flush with the top would leave coincident faces there.
    for i in range(columns):
        for j in range(rows):
            body -= Pos(
                (i - (columns - 1) / 2) * pitch,
                (j - (rows - 1) / 2) * pitch,
                top - pocket_depth,
            ) * Cylinder(
                pocket_diameter / 2,
                pocket_depth + wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    if draft:
        return body

    # Everything that lies wholly in the top face: the ten pocket mouths and the outer
    # rim. The bottom perimeter and the vertical corners stay sharp, which is what keeps
    # the bounding box exactly the stated block size.
    rim = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 1e-6
        and abs(e.bounding_box().max.Z - top) < 1e-6
    )
    return polish(body, rim, chamfer_size)
