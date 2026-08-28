from nurb import Align, Axis, Box, BuildPart, Cone, Cylinder, Locations, Mode, chamfer, part


@part
def bit_block(shank_diameter: float = 6.0, columns: int = 5):
    """A compact upright holder for driver bits.

    shank_diameter: measured width across each bit shank.
    columns: number of pockets across the long direction.
    """
    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2
    wall_thickness = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    lead_in = 0.8
    rows = 2

    # Keep the specified 2 mm walls when a nearby bit diameter is selected.
    pitch = pocket_diameter + wall_thickness
    length = columns * pocket_diameter + (columns - 1) * wall_thickness + 2 * wall_thickness
    width = rows * pocket_diameter + (rows - 1) * wall_thickness + 2 * wall_thickness
    height = floor_thickness + pocket_depth

    pocket_positions = [
        (
            -length / 2 + wall_thickness + pocket_radius + column * pitch,
            -width / 2 + wall_thickness + pocket_radius + row * pitch,
            floor_thickness,
        )
        for row in range(rows)
        for column in range(columns)
    ]

    with BuildPart() as block:
        # Select just the four top exterior edges.  The bottom stays unmodified,
        # preserving both a sharp bed perimeter and the stated overall footprint.
        Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        top_outer_edges = block.part.edges().filter_by_position(Axis.Z, height, height)
        chamfer(top_outer_edges, lead_in)

        # A straight bore and one conical subtraction give every mouth its exact
        # 0.8 mm / 45° lead-in, without rounding any floor or bottom edge.
        with Locations(pocket_positions):
            Cylinder(pocket_radius, pocket_depth - lead_in, mode=Mode.SUBTRACT,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([
            (x, y, height - lead_in) for x, y, _ in pocket_positions
        ]):
            Cone(
                pocket_radius,
                pocket_radius + lead_in,
                lead_in,
                mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    return block.part
