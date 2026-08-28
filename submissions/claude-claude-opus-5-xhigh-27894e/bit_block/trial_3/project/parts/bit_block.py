from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_depth=12.0,
    floor_thickness=3.0,
    wall_thickness=2.0,
    shank_clearance=0.3,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block of upright pockets that driver bits drop into and stand in.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run left to right
    rows: how many pockets run front to back
    pocket_depth: how deep a bit sinks into the block
    floor_thickness: how much solid material sits under the pockets
    wall_thickness: how much material stands between neighbouring pockets, and between the outer pockets and the sides
    shank_clearance: how much wider than a shank each pocket is bored
    chamfer_size: how far the lead-in chamfer cuts back at each pocket mouth and around the top rim
    """
    pocket_diameter = shank_diameter + shank_clearance

    if columns < 1 or rows < 1:
        reject("a block needs at least one pocket", param="columns")
    if pocket_diameter < 2.0:
        raise_at = 2.0 - shank_clearance
        reject(
            f"a {pocket_diameter}mm pocket prints as a smear: raise shank_diameter above {raise_at}",
            param="shank_diameter",
        )
    # Two 45 degree chamfers meeting on one wall need more than 2 * size of face
    # between them, or OCCT drops the whole polish pass.
    if wall_thickness <= 2 * chamfer_size:
        reject(
            f"a {wall_thickness}mm wall cannot carry two {chamfer_size}mm chamfers: "
            f"raise wall_thickness above {2 * chamfer_size}",
            param="wall_thickness",
        )

    pitch = pocket_diameter + wall_thickness
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall_thickness
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall_thickness
    height = floor_thickness + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    # Bore each pocket from above, running the cutter clear of the top face so the
    # mouth is a real cut rather than two coincident planes.
    overshoot = 1.0
    bore = pocket_depth + overshoot
    for column in range(columns):
        for row in range(rows):
            x = (column - (columns - 1) / 2) * pitch
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, height - pocket_depth + bore / 2) * Cylinder(
                pocket_diameter / 2, bore
            )

    if draft:
        return body

    # Only the top face's own edges break: the ten pocket mouths and the outer rim.
    # The bottom perimeter stays sharp so the block's stated size is its real size.
    top = body.bounding_box().max.Z
    concave = concave_edges(body)
    rim = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-4 and e not in concave
    )
    return polish(body, rim, chamfer_size)
