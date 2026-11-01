from nurb import *


@part
def bit_block(shank_diameter=float(measured("shank_diameter")), columns=5):
    """A flat bench block with two rows of upright bit pockets.

    shank_diameter: measured width of the bit shanks; pockets add 0.3 mm clearance.
    columns: number of bit pockets in each of the two rows.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")

    pocket_diameter = shank_diameter + 0.3
    pitch = pocket_diameter + 2.0
    width = (columns - 1) * pitch + pocket_diameter + 4.0
    depth = pitch + pocket_diameter + 4.0
    height = 15.0
    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    for column in range(columns):
        x = (column - (columns - 1) / 2.0) * pitch
        for row in range(2):
            y = (row - 0.5) * pitch
            pocket = Pos(x, y, 3.0) * Cylinder(
                pocket_diameter / 2.0, 12.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - pocket

    top_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7
    )
    return chamfer(top_edges, length=0.8)
