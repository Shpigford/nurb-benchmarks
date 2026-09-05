from nurb import *


@part
def leg_cup():
    """Slip-over workbench foot cup; fit and lift come from measurements.toml."""
    pocket_width = measured("leg_width") + 0.4
    pocket_depth = measured("leg_depth") + 0.4
    lift = measured("lift")
    wall_thickness = 2.0
    pocket_height = 8.0

    outer = Box(
        pocket_width + 2.0 * wall_thickness,
        pocket_depth + 2.0 * wall_thickness,
        lift + pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Every edge defines an exact wall, pocket, or floor dimension. Keep square.
    return outer - pocket
