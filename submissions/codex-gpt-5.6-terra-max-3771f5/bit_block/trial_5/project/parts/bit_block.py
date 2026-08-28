from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """A flat bench block for upright driver bits.

    shank_diameter: measured width across each bit shank
    columns: number of pockets across the block
    """
    if shank_diameter <= 0.0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    block_height = floor_thickness + pocket_depth
    wall_thickness = 2.0
    rows = 2
    mouth_chamfer = 0.8

    # The pitch preserves a 2 mm web as a shank size changes.
    pitch = pocket_diameter + wall_thickness
    block_width = columns * pocket_diameter + (columns + 1) * wall_thickness
    block_depth = rows * pocket_diameter + (rows + 1) * wall_thickness

    body = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Only the four horizontal perimeter edges at the top are chamfered. The
    # bottom perimeter remains the exact stated rectangular footprint.
    top_edges = body.edges().filter_by(
        lambda edge: (
            abs(edge.bounding_box().min.Z - block_height) < 1e-7
            and abs(edge.bounding_box().max.Z - block_height) < 1e-7
        )
    )
    body = chamfer(top_edges, mouth_chamfer)

    straight_depth = pocket_depth - mouth_chamfer
    for row in range(rows):
        y = wall_thickness + pocket_radius + row * pitch
        for column in range(columns):
            x = wall_thickness + pocket_radius + column * pitch

            # The straight bore starts at the 3 mm floor. A separate cone makes
            # the required 0.8 mm radial and vertical 45-degree lead-in.
            bore = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                straight_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            lead_in = Pos(x, y, floor_thickness + straight_depth) * Cone(
                pocket_radius,
                pocket_radius + mouth_chamfer,
                mouth_chamfer,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            body = body - bore
            body = body - lead_in

    return body
