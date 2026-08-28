from nurb import *


@part
def bit_block(
    shank_diameter: float = measured("shank_diameter"),
    columns: int = 5,
):
    """Bench block for holding driver bits upright.

    shank_diameter: measured width across each bit shank; pockets add 0.3 mm.
    columns: number of bit pockets across the long side of the block.
    """
    pocket_clearance = 0.3
    pocket_depth = 12.0
    floor_thickness = 3.0
    edge_material = 2.0
    web_thickness = 2.0
    mouth_chamfer = 0.8
    rows = 2

    if columns < 1:
        reject("columns must be at least 1", "columns")
    if shank_diameter <= 0:
        reject("shank_diameter must be positive", "shank_diameter")

    pocket_diameter = shank_diameter + pocket_clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + web_thickness
    block_width = (columns - 1) * pitch + pocket_diameter + 2.0 * edge_material
    block_depth = (rows - 1) * pitch + pocket_diameter + 2.0 * edge_material
    block_height = pocket_depth + floor_thickness

    body = Box(block_width, block_depth, block_height)
    pocket_center_z = -block_height / 2.0 + floor_thickness + pocket_depth / 2.0
    first_x = -block_width / 2.0 + edge_material + pocket_radius
    first_y = -block_depth / 2.0 + edge_material + pocket_radius

    for column in range(columns):
        for row in range(rows):
            pocket = Cylinder(pocket_radius, pocket_depth).translate(
                (
                    first_x + column * pitch,
                    first_y + row * pitch,
                    pocket_center_z,
                )
            )
            body = body - pocket

    # These are precisely the pocket mouths and the top outer perimeter. Chamfering
    # them together gives the requested 0.8 mm, 45 degree lead-ins while preserving
    # the lower perimeter as the exact, sharp bounding box.
    top = block_height / 2.0
    top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z >= top - 0.01
    )
    return chamfer(top_edges, mouth_chamfer)
