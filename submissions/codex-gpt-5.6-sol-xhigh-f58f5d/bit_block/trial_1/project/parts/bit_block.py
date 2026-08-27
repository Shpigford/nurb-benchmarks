from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5):
    """A compact bench block that stores driver bits upright.

    shank_diameter: measured width of each bit's round shank
    columns: number of bit pockets in each of the two rows
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    clearance = 0.3
    material_between_pockets = 2.0
    side_material = 2.0
    rows = 2
    pocket_depth = 12.0
    floor_thickness = 3.0
    chamfer_size = 0.8

    pocket_diameter = shank_diameter + clearance
    pitch = pocket_diameter + material_between_pockets
    width = (columns - 1) * pitch + pocket_diameter + 2.0 * side_material
    depth = (rows - 1) * pitch + pocket_diameter + 2.0 * side_material
    height = pocket_depth + floor_thickness

    body = Box(
        width,
        depth,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    for column in range(columns):
        x = (column - (columns - 1) / 2.0) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2.0) * pitch
            pocket = Pos(x, y, floor_thickness) * Cylinder(
                pocket_diameter / 2.0,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - pocket

    # All and only the edges lying in the top plane are dressed: this selects
    # the ten pocket mouths and the outer top perimeter, while preserving the
    # pocket floors, vertical corners, and sharp bed-contact perimeter.
    top_edges = body.edges().filter_by_position(Axis.Z, height, height)
    return chamfer(top_edges, chamfer_size)
