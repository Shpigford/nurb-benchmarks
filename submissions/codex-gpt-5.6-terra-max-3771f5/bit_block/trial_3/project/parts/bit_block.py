from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block that stores driver bits upright.

    shank_diameter: measured width of the bit shanks that the pockets hold
    columns: number of pockets across the long side of the block
    """
    pocket_clearance = 0.3
    pocket_depth = 12.0
    floor_thickness = 3.0
    wall_thickness = 2.0
    pocket_chamfer = 0.8
    rows = 2

    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")

    pocket_diameter = shank_diameter + pocket_clearance
    pitch = pocket_diameter + wall_thickness
    length = 2 * wall_thickness + pocket_diameter + (columns - 1) * pitch
    depth = 2 * wall_thickness + pocket_diameter + (rows - 1) * pitch
    height = floor_thickness + pocket_depth
    pocket_radius = pocket_diameter / 2

    body = Box(
        length,
        depth,
        height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    for column in range(columns):
        for row in range(rows):
            center_x = wall_thickness + pocket_radius + column * pitch
            center_y = wall_thickness + pocket_radius + row * pitch
            pocket = Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).translate((center_x, center_y, floor_thickness))
            body -= pocket

    if draft:
        return body

    # All edges lying in the top plane are either an outer top edge or a pocket
    # mouth. Chamfering exactly this set leaves the bottom perimeter sharp.
    top_edges = body.edges().filter_by(
        lambda edge: (
            abs(edge.bounding_box().min.Z - height) < 0.001
            and abs(edge.bounding_box().max.Z - height) < 0.001
        )
    )
    return chamfer(top_edges, pocket_chamfer)
