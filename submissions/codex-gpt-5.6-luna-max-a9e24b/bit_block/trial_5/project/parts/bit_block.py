"""Parametric upright driver-bit bench block."""

from nurb import *


_DEFAULT_SHANK_DIAMETER = float(measured("shank_diameter"))


@part
def bit_block(
    shank_diameter=_DEFAULT_SHANK_DIAMETER,
    columns=5,
    draft=False,
):
    """Bench block with a two-row grid of upright driver-bit pockets.

    shank_diameter: diameter of the bit shank being held
    columns: number of pockets across the block
    """
    if shank_diameter <= 0:
        reject("shank_diameter must be greater than 0 mm", param="shank_diameter")
    if columns < 1:
        reject("columns must be at least 1", param="columns")

    pocket_diameter = shank_diameter + 0.3
    wall = 2.0
    rows = 2
    pitch = pocket_diameter + wall
    pocket_depth = 12.0
    floor_thickness = 3.0
    height = floor_thickness + pocket_depth

    block_width = columns * pocket_diameter + (columns + 1) * wall
    block_depth = rows * pocket_diameter + (rows + 1) * wall

    block = Box(
        block_width,
        block_depth,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    first_x = -block_width / 2 + wall + pocket_diameter / 2
    first_y = -block_depth / 2 + wall + pocket_diameter / 2
    for column in range(columns):
        for row in range(rows):
            pocket = Pos(
                first_x + column * pitch,
                first_y + row * pitch,
                floor_thickness,
            ) * Cylinder(
                pocket_diameter / 2,
                pocket_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            block = block - pocket

    if draft:
        return block

    top_face = block.faces().sort_by(Axis.Z)[-1]
    return chamfer(top_face.edges(), length=0.8)
