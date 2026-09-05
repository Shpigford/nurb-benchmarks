from nurb import *


@part
def bit_block(shank_diameter=float(measured("shank_diameter")), columns=5):
    """Bench block with two rows of upright driver-bit pockets.

    shank_diameter: measured width across a bit's shank, before 0.3 mm clearance.
    columns: number of pockets along each of the two rows.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter < 1.7:
        reject("shank_diameter must be at least 1.7 mm for a 2 mm pocket", param="shank_diameter")

    pocket_diameter = shank_diameter + 0.3
    pitch = pocket_diameter + 2.0
    width = (columns - 1) * pitch + pocket_diameter + 4.0
    depth = pitch + pocket_diameter + 4.0
    height = 15.0
    floor_thickness = 3.0

    body = Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for column in range(columns):
        x = (column - (columns - 1) / 2) * pitch
        for row in range(2):
            y = (row - 0.5) * pitch
            body -= Pos(x, y, floor_thickness) * Cylinder(
                pocket_diameter / 2, height - floor_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # Only edges in the top plane: all mouths and the outer perimeter.
    # Exact chamfer, so a failed edge cannot silently retain a sharp mouth.
    top_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - height) < 1e-7
        and abs(edge.bounding_box().max.Z - height) < 1e-7
    )
    return chamfer(top_edges, length=0.8)
