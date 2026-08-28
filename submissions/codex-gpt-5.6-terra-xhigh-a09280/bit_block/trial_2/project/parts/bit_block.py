from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A compact, upright holder for driver bits.

    shank_diameter: measured width of the bit shanks the pockets hold.
    columns: number of pockets across the front-to-back two-row grid.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")

    clearance = 0.3
    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    wall_thickness = 2.0
    pitch = pocket_diameter + wall_thickness
    rows = 2

    width = columns * pocket_diameter + (columns - 1) * wall_thickness + 2.0 * wall_thickness
    depth = rows * pocket_diameter + (rows - 1) * wall_thickness + 2.0 * wall_thickness
    body = Box(width, depth, floor_thickness + pocket_depth)

    for column in range(columns):
        x = (column - (columns - 1) / 2.0) * pitch
        for row in range(rows):
            y = (row - (rows - 1) / 2.0) * pitch
            # Box and Cylinder are centred on Z, so this places the 12 mm cut
            # exactly on the top face and leaves the specified 3 mm floor.
            pocket = Pos(x, y, floor_thickness / 2.0) * Cylinder(pocket_radius, pocket_depth)
            body = body - pocket

    if draft:
        return body

    top = body.bounding_box().max.Z
    top_edges = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - top) < 0.001
        and abs(edge.bounding_box().max.Z - top) < 0.001
    )
    return chamfer(top_edges, 0.8)
