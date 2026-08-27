"""Bench block for storing hex driver bits upright."""

from build123d import Align, Box, Cone, Cylinder, Pos, chamfer
from nurb import part


@part
def bit_block(
    shank_diameter: float = 6.0,
    columns: int = 5,
):
    """A compact two-row holder for straight-shank driver bits.

    shank_diameter: measured width of each bit shank
    columns: number of bit pockets in each row
    """
    clearance = 0.3
    material_between_pockets = 2.0
    material_to_sides = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    rows = 2

    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2.0
    pitch = pocket_diameter + material_between_pockets

    block_width = columns * pocket_diameter + (columns - 1) * material_between_pockets + 2.0 * material_to_sides
    block_depth = rows * pocket_diameter + (rows - 1) * material_between_pockets + 2.0 * material_to_sides
    block_height = pocket_depth + floor_thickness

    block = Box(
        block_width,
        block_depth,
        block_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Only the four top perimeter edges are chamfered. Keeping the bottom four
    # horizontal edges out of this selection preserves the exact footprint.
    top_edges = [
        edge
        for edge in block.edges()
        if abs(edge.center().Z - block_height) < 1e-7
    ]
    block = chamfer(top_edges, lead_in)

    first_x = -0.5 * (columns - 1) * pitch
    first_y = -0.5 * (rows - 1) * pitch
    straight_depth = pocket_depth - lead_in

    for row in range(rows):
        for column in range(columns):
            x = first_x + column * pitch
            y = first_y + row * pitch

            straight_bore = Pos(x, y, floor_thickness) * Cylinder(
                pocket_radius,
                straight_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

            # Extend the conical cutter microscopically above the top to make
            # the opening unambiguous while retaining the exact 45-degree
            # intersection and 0.8 mm lead-in at z == block_height.
            cutter_overrun = 0.01
            mouth = Pos(x, y, block_height - lead_in) * Cone(
                pocket_radius,
                pocket_radius + lead_in + cutter_overrun,
                lead_in + cutter_overrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

            block = block - straight_bore - mouth

    return block
