from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
):
    """A compact bench block that stores driver bits upright.

    shank_diameter: measured width of the driver-bit shank
    columns: number of pockets across the block
    """
    if shank_diameter <= 0.0:
        reject(
            "shank_diameter must be greater than 0mm",
            param="shank_diameter",
        )
    if columns < 1:
        reject(
            "columns must be at least 1",
            param="columns",
        )

    rows = 2
    fit_clearance = 0.3
    wall = 2.0
    floor = 3.0
    pocket_depth = 12.0
    lead_in = 0.8

    pocket_diameter = shank_diameter + fit_clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + wall
    width = pocket_diameter + (columns - 1) * pitch + 2.0 * wall
    depth = pocket_diameter + (rows - 1) * pitch + 2.0 * wall
    height = floor + pocket_depth

    block = Box(
        width,
        depth,
        height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    top_edges = block.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > height - 1e-7
    )
    block = chamfer(top_edges, length=lead_in)

    first_center = wall + pocket_radius
    cutter_overlap = 0.1
    for row in range(rows):
        y = first_center + row * pitch
        for column in range(columns):
            x = first_center + column * pitch

            straight_pocket = Cylinder(
                pocket_radius,
                pocket_depth + cutter_overlap,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).translate((x, y, floor))
            lead_in_cut = Cone(
                pocket_radius,
                pocket_radius + lead_in + cutter_overlap,
                lead_in + cutter_overlap,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).translate((x, y, height - lead_in))

            block = block - (straight_pocket + lead_in_cut)

    return block
