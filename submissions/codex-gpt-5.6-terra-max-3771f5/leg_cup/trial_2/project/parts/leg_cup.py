from nurb import *


@part
def leg_cup():
    """Slip-over leveling cup for a rectangular workbench leg.

    The pocket has 0.4 mm total clearance around the measured leg; the solid
    floor raises the bench by the provisional lift measurement.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_height = 8.0
    pocket_width = leg_width + clearance
    pocket_depth = leg_depth + clearance

    with BuildPart() as cup:
        Box(
            pocket_width + 2 * wall_thickness,
            pocket_depth + 2 * wall_thickness,
            lift + pocket_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations((0, 0, lift)):
                Box(
                    pocket_width,
                    pocket_depth,
                    pocket_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    return cup.part
