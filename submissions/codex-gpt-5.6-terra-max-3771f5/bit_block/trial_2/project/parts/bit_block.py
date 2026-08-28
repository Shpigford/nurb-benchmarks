from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block that stores driver bits upright.

    shank_diameter: measured width across each bit shank.
    columns: number of bit pockets across the long side.
    """
    if columns < 1:
        reject("columns must be at least 1", param="columns")
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0", param="shank_diameter")

    rows = 2
    pocket_clearance = 0.3
    pocket_diameter = shank_diameter + pocket_clearance
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    total_height = floor_thickness + pocket_depth
    wall_thickness = 2.0
    lead_in = 0.8

    pitch = pocket_diameter + wall_thickness
    length = 2.0 * wall_thickness + pocket_diameter + (columns - 1) * pitch
    width = 2.0 * wall_thickness + pocket_diameter + (rows - 1) * pitch

    body = Box(
        length,
        width,
        total_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    top_perimeter = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > total_height - 0.001
    )
    body = chamfer(top_perimeter, lead_in)

    for row in range(rows):
        for column in range(columns):
            x = wall_thickness + pocket_radius + column * pitch
            y = wall_thickness + pocket_radius + row * pitch
            straight_pocket = Cylinder(
                pocket_radius,
                pocket_depth - lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).translate((x, y, floor_thickness))
            pocket_lead_in = Cone(
                pocket_radius,
                pocket_radius + lead_in,
                lead_in,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ).translate((x, y, total_height - lead_in))
            body = body - straight_pocket - pocket_lead_in

    return body
