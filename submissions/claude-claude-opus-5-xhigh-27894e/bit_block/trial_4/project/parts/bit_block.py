from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    shank_clearance=0.3,
    pocket_depth=12.0,
    wall=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that holds driver bits shank-down in a grid of pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets run along the long side
    rows: how many pockets run across the short side
    shank_clearance: extra width in the pocket so a bit drops in without forcing
    pocket_depth: how deep a bit sinks into the block
    wall: material between neighbouring pockets, and from a pocket out to the side
    floor_thickness: solid material under the pockets
    chamfer_size: the lead-in bevel at each pocket mouth and around the top edge
    """
    pocket_dia = shank_diameter + shank_clearance
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} makes a {pocket_dia:.2f}mm pocket; "
            "a bore under 2mm prints closed. Raise it above "
            f"{2.0 - shank_clearance:.2f}",
            param="shank_diameter",
        )
    if columns < 1 or rows < 1:
        reject(
            f"a {columns} x {rows} grid holds nothing: both counts start at 1",
            param="columns" if columns < 1 else "rows",
        )
    # Kernel rule: two chamfered convex edges need more than 2 * chamfer_size of
    # face between them, and `wall` is exactly what sits between two pocket rims.
    if wall <= 2 * chamfer_size:
        reject(
            f"wall {wall} leaves less than {2 * chamfer_size:.2f}mm between two "
            f"{chamfer_size}mm pocket chamfers, so they collide. Raise it above "
            f"{2 * chamfer_size:.2f}",
            param="wall",
        )
    if floor_thickness < 2.0:
        reject(
            f"floor_thickness {floor_thickness} is under the 2mm minimum wall; "
            "the pockets would punch through. Raise it above 2.0",
            param="floor_thickness",
        )
    if pocket_depth <= chamfer_size:
        reject(
            f"pocket_depth {pocket_depth} is not deeper than the {chamfer_size}mm "
            "lead-in, so there is no pocket left to hold a bit",
            param="pocket_depth",
        )

    # Pitch is a pocket plus one wall, so the same `wall` sets both the material
    # between neighbours and the material out to the sides.
    pitch = pocket_dia + wall
    length = (columns - 1) * pitch + pocket_dia + 2 * wall
    width = (rows - 1) * pitch + pocket_dia + 2 * wall
    height = pocket_depth + floor_thickness

    body = Pos(0, 0, height / 2) * Box(length, width, height)

    # Pockets open straight up and stop on a flat floor `floor_thickness` above
    # the bed: a vertical blind bore is self-supporting and needs no roof.
    x0 = -(columns - 1) * pitch / 2
    y0 = -(rows - 1) * pitch / 2
    for col in range(columns):
        for row in range(rows):
            body -= Pos(
                x0 + col * pitch,
                y0 + row * pitch,
                height - pocket_depth / 2,
            ) * Cylinder(pocket_dia / 2, pocket_depth)

    if draft:
        return body

    # Everything that gets broken lies in the top plane: the ten pocket mouths
    # and the outer perimeter. The bottom perimeter stays sharp so the block
    # meets the bed on its full footprint, and the pocket floors are concave.
    top = height
    rim = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 1e-4
        and abs(e.bounding_box().max.Z - top) < 1e-4
    )
    return polish(body, rim, chamfer_size)
