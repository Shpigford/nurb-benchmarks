from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5, draft=False):
    """Bench block that holds driver bits upright in round pockets.

    shank_diameter: how wide the bits' shanks are across
    columns: how many pockets sit side by side across the block
    """
    rows = 2
    pocket_clearance = 0.3  # slack a printed pocket needs over the shank
    wall_gap = 2.0  # material between neighbouring pocket walls
    edge_margin = 2.0  # material from the outermost pocket wall to the block's side
    floor_thickness = 3.0
    pocket_depth = 12.0
    chamfer_size = 0.8

    pocket_dia = shank_diameter + pocket_clearance
    pocket_radius = pocket_dia / 2
    pitch = pocket_dia + wall_gap

    width = (columns - 1) * pitch + pocket_dia + 2 * edge_margin
    depth = (rows - 1) * pitch + pocket_dia + 2 * edge_margin
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height)

    top_z = height / 2
    pocket_z = top_z - pocket_depth / 2
    x_positions = [(-(columns - 1) / 2 + i) * pitch for i in range(columns)]
    y_positions = [(-(rows - 1) / 2 + j) * pitch for j in range(rows)]

    for x in x_positions:
        for y in y_positions:
            body -= Pos(x, y, pocket_z) * Cylinder(pocket_radius, pocket_depth)

    if draft:
        return body

    # Only the pocket mouths and the top outer perimeter break; the bottom
    # perimeter and every vertical edge stay sharp. Both live entirely on the
    # top face, so its own edge list is exactly the set to chamfer.
    top_face = body.faces().sort_by(Axis.Z)[-1]
    return polish(body, top_face.edges(), chamfer_size)
