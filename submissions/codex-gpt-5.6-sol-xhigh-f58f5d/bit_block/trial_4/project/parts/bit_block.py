from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
):
    """A bench block that stores driver bits upright.

    shank_diameter: measured width of each driver's round shank
    columns: number of bit pockets in each of the two rows
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    clearance = 0.3
    wall = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    rows = 2

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    edge_offset = pocket_radius + wall

    block_width = 2.0 * edge_offset + (columns - 1) * pitch
    block_depth = 2.0 * edge_offset + (rows - 1) * pitch
    block_height = floor_thickness + pocket_depth

    body = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Break only the four edges around the top outer perimeter. The bottom and
    # vertical perimeter edges remain sharp.
    top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > block_height - 0.01
    )
    body = chamfer(top_edges, lead_in)

    # Each pocket is a full-depth cylinder plus a 45-degree conical lead-in.
    # The cylinder establishes the exact flat floor at z=3 and exact 12mm depth.
    for row in range(rows):
        for column in range(columns):
            center = (
                edge_offset + column * pitch,
                edge_offset + row * pitch,
            )
            pocket = Cylinder(
                pocket_radius,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).move(Location((center[0], center[1], floor_thickness)))
            lead = Cone(
                pocket_radius,
                pocket_radius + lead_in,
                lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).move(Location((center[0], center[1], block_height - lead_in)))
            body = body - pocket - lead

    return body
