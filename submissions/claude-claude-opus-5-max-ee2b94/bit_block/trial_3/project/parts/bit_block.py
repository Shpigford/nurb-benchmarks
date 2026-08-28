from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall_between_pockets=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits shank-down in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run along the length of the block
    rows: how many pockets run across the width of the block
    pocket_clearance: how much wider than a shank each pocket is bored, so bits drop in
    pocket_depth: how far a bit drops before it stands on the pocket floor
    wall_between_pockets: material between neighbouring pockets, and from the outer
        pockets to the sides of the block
    floor_thickness: solid material under the pocket floors
    chamfer_size: the lead-in break at each pocket mouth and around the top edge
    """
    pocket_diameter = shank_diameter + pocket_clearance

    if columns < 1 or rows < 1:
        reject(
            "a block needs at least one pocket in each direction",
            param="columns" if columns < 1 else "rows",
        )
    if pocket_clearance <= 0:
        reject(
            f"pocket_clearance {pocket_clearance} bores the pocket at or under the "
            f"{shank_diameter}mm shank, so no bit drops in: raise it above 0",
            param="pocket_clearance",
        )
    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket is under the 2mm floor where a bore "
            "prints as a smear: raise shank_diameter",
            param="shank_diameter",
        )
    # Two chamfered mouths facing each other need more than 2 * chamfer_size of flat
    # between them or OCCT drops the whole polish pass.
    if wall_between_pockets <= 2 * chamfer_size:
        reject(
            f"wall_between_pockets {wall_between_pockets} leaves no flat between two "
            f"{chamfer_size}mm mouth chamfers: raise it above {2 * chamfer_size}",
            param="wall_between_pockets",
        )

    # Pitch is one pocket plus one wall, so the material between neighbours is the wall
    # everywhere: between pockets and from the outer pockets to the sides alike.
    pitch = pocket_diameter + wall_between_pockets
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall_between_pockets
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall_between_pockets
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    pocket = Cylinder(
        pocket_diameter / 2,
        pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    first_x = -pitch * (columns - 1) / 2
    first_y = -pitch * (rows - 1) / 2
    for column in range(columns):
        for row in range(rows):
            body -= Pos(
                first_x + column * pitch,
                first_y + row * pitch,
                floor_thickness,
            ) * pocket

    if draft:
        return body

    # Everything lying in the top face: the ten pocket mouths and the outer perimeter.
    # The vertical corners and the whole bottom perimeter stay sharp, so the block sits
    # flat on the bench and its bounding box is the size on the card.
    top = body.bounding_box().max.Z
    rim = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-6
    )
    return polish(body, rim, chamfer_size)
