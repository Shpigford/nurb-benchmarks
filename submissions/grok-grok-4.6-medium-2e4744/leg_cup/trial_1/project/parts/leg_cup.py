from nurb import *

# Slip around the measured leg, wall all around the pocket, how deep the foot sits.
_SLIP = 0.4
_WALL = 2.0
_POCKET_DEPTH = 8.0


@part
def leg_cup(draft=False):
    """Slip-over foot cup that lifts a short workbench leg until the bench sits level.

    The cup prints pocket-up. Inner pocket, walls, and floor all track measurements.toml
    (leg_width, leg_depth, lift). lift is provisional until someone measures the wobble.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + _SLIP
    pocket_depth = leg_depth + _SLIP
    outer_width = pocket_width + 2 * _WALL
    outer_depth = pocket_depth + 2 * _WALL
    height = lift + _POCKET_DEPTH

    body = Box(
        outer_width,
        outer_depth,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Stick the cutter a hair through the rim so the pocket opens straight up
    # and nothing roofs it. The floor of the cut stays at z = lift.
    cutter = Box(
        pocket_width,
        pocket_depth,
        _POCKET_DEPTH + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cutter = cutter.moved(Location((0, 0, lift)))
    cup = body - cutter

    if draft:
        return cup
    # Mating pocket and bed stay sharp: lead-in on the mouth and polish on the
    # first layer are both forbidden, and 2 mm walls have no room for a 1 mm
    # chamfer on both the inner and outer rim.
    return cup
