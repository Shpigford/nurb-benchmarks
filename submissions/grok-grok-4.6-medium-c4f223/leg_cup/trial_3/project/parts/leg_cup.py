from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts a short workbench leg until the bench sits level.

    The pocket is the measured leg plus 0.4 mm of slip-on clearance, 8.0 mm deep,
    with 2.0 mm walls. Floor thickness is `lift` from measurements.toml so a
    later caliper reading rebuilds the part without editing this file.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_w = leg_width + clearance
    pocket_d = leg_depth + clearance
    outer_w = pocket_w + 2.0 * wall
    outer_d = pocket_d + 2.0 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Overcut the open end so the pocket is not roofed by a coplanar boolean.
    cutter = Pos(0, 0, lift) * Box(
        pocket_w,
        pocket_d,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cup = body - cutter
    if draft:
        return cup
    # Fit faces stay sharp: inner size, wall thickness, and bed contact are exact.
    # A 1 mm polish on a 2 mm rim would also collapse the wall at the lip.
    return cup
