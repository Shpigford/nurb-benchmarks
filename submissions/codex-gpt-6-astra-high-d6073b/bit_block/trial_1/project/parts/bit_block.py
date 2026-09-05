from nurb import *


@part
def bit_block(shank_diameter=float(measured("shank_diameter")), columns=5):
    """A flat bench block with two rows of upright driver-bit pockets.

    shank_diameter: measured bit width; pockets add 0.3 mm clearance.
    columns: number of pockets along each of the two rows.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter < 1.7:
        reject("shank_diameter must be at least 1.7 mm for printable pockets",
               param="shank_diameter")

    pocket_diameter = shank_diameter + 0.3
    wall = 2.0
    pitch = pocket_diameter + wall
    rows = 2
    width = columns * pocket_diameter + (columns + 1) * wall
    depth = rows * pocket_diameter + (rows + 1) * wall
    floor = 3.0
    pocket_depth = 12.0
    height = floor + pocket_depth

    body = Box(width, depth, height,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    for column in range(columns):
        x = (column - (columns - 1) / 2) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2) * pitch
            body -= Pos(x, y, floor) * Cylinder(
                pocket_diameter / 2, pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Only the coplanar mouth circles and outer top edges receive lead-ins.
    # Use an exact chamfer so no requested edge can be silently skipped.
    top_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7)
    return chamfer(top_edges, length=0.8)
