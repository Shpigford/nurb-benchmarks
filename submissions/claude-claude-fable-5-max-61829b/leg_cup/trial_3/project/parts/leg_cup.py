from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """Slip-over foot cup for the workbench's short leg: the foot drops into the
    pocket from above and the solid floor under it lifts the bench level.

    wall_thickness: how thick the cup's four walls are
    pocket_depth: how far the leg's foot drops into the cup
    leg_clearance: total extra room across the pocket so the foot drops in from above
    """
    # Every fit dimension comes from measurements.toml, never from a number here.
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")  # provisional until someone measures the gap at the shop

    if lift <= 0:
        reject(
            f"lift {lift} leaves no floor under the foot, so the cup lifts nothing: "
            "record the gap under the short leg in measurements.toml as a positive value"
        )

    pocket_width = leg_width + leg_clearance
    pocket_length = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    height = lift + pocket_depth

    # Flat bottom on the bed at z=0, pocket opening straight up.
    on_bed = (Align.CENTER, Align.CENTER, Align.MIN)
    block = Box(outer_width, outer_length, height, align=on_bed)
    # The pocket runs 1mm past the rim so the cut never leaves a coplanar sliver.
    pocket = Pos(0, 0, lift) * Box(pocket_width, pocket_length, pocket_depth + 1.0, align=on_bed)
    cup = block - pocket
    if draft:
        return cup

    # Polish only the four outer vertical corners. The rim is the pocket's mouth
    # (fit-critical, never chamfered), the pocket's own edges are concave, and the
    # bottom edges lie on the bed.
    outer_corners = (
        cup.edges()
        .filter_by(Axis.Z)
        .filter_by(lambda e: abs(e.center().X) > pocket_width / 2)
    )
    return polish(cup, outer_corners, 1.0)
