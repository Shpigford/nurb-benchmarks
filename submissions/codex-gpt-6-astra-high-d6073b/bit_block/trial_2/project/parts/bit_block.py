from nurb import *


@part
def bit_block(shank_diameter=float(measured("shank_diameter")), columns=5):
    """A flat bench block with two rows of upright driver-bit pockets.

    shank_diameter: measured width of the bit shank, before 0.3 mm clearance.
    columns: number of pockets in each of the two rows.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter < 1.7:
        reject("shank_diameter must be at least 1.7 mm", param="shank_diameter")

    pocket_diameter = shank_diameter + 0.3
    wall = 2.0
    pitch = pocket_diameter + wall
    rows = 2
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall
    floor_thickness = 3.0
    pocket_depth = 12.0
    height = floor_thickness + pocket_depth

    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for column in range(columns):
        x = (column - (columns - 1) / 2) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, floor_thickness) * Cylinder(
                pocket_diameter / 2,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # Only edges lying in the top plane: all mouths and the outer perimeter.
    # A single exact chamfer preserves the sharp floor, bottom and vertical edges.
    top_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7
    )
    return chamfer(top_edges, length=0.8)
