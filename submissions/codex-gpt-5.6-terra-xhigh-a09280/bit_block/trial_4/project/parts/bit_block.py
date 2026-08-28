from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A benchtop holder for driver bits.

    shank_diameter: measured width across each bit shank; pockets add 0.3 mm clearance.
    columns: number of pockets across the long side of the block.
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    rows = 2
    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    total_height = floor_thickness + pocket_depth
    material_between_pockets = 2.0
    side_wall = 2.0
    chamfer_size = 0.8
    pitch = pocket_diameter + material_between_pockets

    block_length = columns * pocket_diameter + (columns - 1) * material_between_pockets + 2.0 * side_wall
    block_width = rows * pocket_diameter + (rows - 1) * material_between_pockets + 2.0 * side_wall

    # Only the four horizontal edges at the top are chamfered. Keeping this
    # operation ahead of the cuts leaves the bed-facing perimeter perfectly sharp.
    block = Box(block_length, block_width, total_height, align=(Align.MIN, Align.MIN, Align.MIN))
    top_outer_edges = block.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z >= total_height - 0.001
    )
    body = chamfer(top_outer_edges, chamfer_size)

    # A cylindrical bore establishes the fit diameter and depth. The shallow cone
    # removes precisely a 0.8 x 45-degree lead-in at each open mouth.
    pockets = None
    for row in range(rows):
        for column in range(columns):
            x = side_wall + pocket_radius + column * pitch
            y = side_wall + pocket_radius + row * pitch
            bore = Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).moved(Location((x, y, floor_thickness)))
            lead_in = Cone(
                pocket_radius,
                pocket_radius + chamfer_size,
                chamfer_size,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).moved(Location((x, y, total_height - chamfer_size)))
            pocket = bore + lead_in
            pockets = pocket if pockets is None else pockets + pocket

    return body - pockets
