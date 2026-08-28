from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    shank_clearance=0.3,
    pocket_depth=12.0,
    material_between_pockets=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run left to right
    rows: how many pockets run front to back
    shank_clearance: extra width the pocket carries over the shank so a bit drops in
    pocket_depth: how deep a bit sinks into the block
    material_between_pockets: plastic left between neighbouring pockets, and around the outside
    floor_thickness: solid plastic under the pockets
    chamfer_size: the lead-in taken off each pocket mouth and off the top outer edges
    """
    pocket_diameter = shank_diameter + shank_clearance
    wall = material_between_pockets

    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket prints as a smear; raise shank_diameter "
            f"above {2.0 - shank_clearance:.2f}",
            param="shank_diameter",
        )
    # Two chamfered mouths need more than 2 * chamfer_size of top face between them,
    # or OCCT drops the whole polish pass rather than one edge of it.
    if wall <= 2.0 * chamfer_size:
        reject(
            f"{wall:.2f}mm between pockets leaves no landing for two {chamfer_size:.2f}mm "
            f"chamfers; raise material_between_pockets above {2.0 * chamfer_size:.2f}",
            param="material_between_pockets",
        )

    pitch = pocket_diameter + wall
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall
    height = floor_thickness + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    for i in range(columns):
        for j in range(rows):
            x = (i - (columns - 1) / 2) * pitch
            y = (j - (rows - 1) / 2) * pitch
            centre = height - pocket_depth / 2
            body -= Pos(x, y, centre) * Cylinder(pocket_diameter / 2, pocket_depth)

    if draft:
        return body

    # Everything lying in the top plane: the four outer edges and the ten pocket mouths.
    # Nothing else is broken, so the bottom perimeter stays sharp and the stated
    # bounding box is the box the part actually occupies.
    top = height
    mouths = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6 and e.bounding_box().max.Z < top + 1e-6
    )
    return polish(body, mouths, chamfer_size)
