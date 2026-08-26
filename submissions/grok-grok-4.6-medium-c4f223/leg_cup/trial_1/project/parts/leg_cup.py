from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts a short workbench leg until the bench sits level.

    The rectangular pocket follows the measured leg plus 0.4 mm of clearance so the
    foot drops in from above. Floor thickness is `lift` from measurements.toml, not a
    number baked into this file, because how much the bench needs was never calipered.

    lift: thickness of the solid floor under the pocket, which is how far the short
    leg is raised
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall = 2.0
    pocket_depth = 8.0
    pocket_width = leg_width + 0.4
    pocket_length = leg_depth + 0.4
    outer_width = pocket_width + 2.0 * wall
    outer_length = pocket_length + 2.0 * wall
    height = lift + pocket_depth

    if lift < 1.0:
        reject(
            f"lift {lift} is under 1.0 mm: the floor would not print as a solid pad",
            param=None,
        )

    body = Box(outer_width, outer_length, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Extra height so the cut breaks the top face cleanly; the pocket still ends at the rim.
    cutter = Box(
        pocket_width,
        pocket_length,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).move(Location((0, 0, lift)))
    cup = body - cutter
    if draft:
        return cup
    # Sharp inner walls and a square rim are the fit. Polish would open the pocket at
    # the rim and cut the inner corners, so the mating size would no longer be exact.
    return cup
