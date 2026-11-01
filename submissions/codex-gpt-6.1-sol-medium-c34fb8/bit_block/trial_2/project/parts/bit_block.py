from nurb import *


@part
def bit_block(shank_diameter=float(measured("shank_diameter")), columns=5):
    """Bench block with upright, flat-bottomed driver-bit pockets.

    shank_diameter: measured width of the driver bit shanks, in mm.
    columns: number of pockets along each of the two rows.
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than zero", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least one", param="columns")

    pocket_diameter = shank_diameter + 0.3
    pitch = pocket_diameter + 2.0
    width = columns * pocket_diameter + (columns - 1) * 2.0 + 4.0
    depth = 2 * pocket_diameter + 2.0 + 4.0
    height = 15.0
    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    for column in range(columns):
        x = (column - (columns - 1) / 2) * pitch
        for row in range(2):
            y = (row - 0.5) * pitch
            pocket = Pos(x, y, 3.0) * Cylinder(
                pocket_diameter / 2, 12.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - pocket

    # Only the coplanar upper edges: all mouths and the outside perimeter.
    # Exact chamfer, rather than a best-effort polish that might skip an edge.
    upper_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7
    )
    return chamfer(upper_edges, length=0.8)
