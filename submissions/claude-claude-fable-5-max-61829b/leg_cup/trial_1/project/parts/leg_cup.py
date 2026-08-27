from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, gap_around_leg=0.4, draft=False):
    """A cup that slips over the foot of the workbench's short leg and lifts it level.

    wall_thickness: how thick the cup's four walls are
    pocket_depth: how far the leg's foot drops into the cup
    gap_around_leg: extra room in the pocket so the leg slips in by hand
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    if lift < 1.0:
        reject(f"lift {lift} is under the 1.0mm floor the printer lays reliably: a gap that small wants a washer under the leg, or measure it again and update measurements.toml")
    if wall_thickness < 1.0:
        reject("wall_thickness under 1.0 is a single perimeter and will split when the leg is dropped in: raise it", param="wall_thickness")
    if pocket_depth <= 0:
        reject("pocket_depth must be positive: it is how far the foot drops into the cup", param="pocket_depth")
    if gap_around_leg < 0:
        reject("gap_around_leg cannot be negative: the pocket would be narrower than the leg", param="gap_around_leg")

    pocket_width = leg_width + gap_around_leg
    pocket_length = leg_depth + gap_around_leg
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(outer_width, outer_length, height)
    # The pocket runs past the rim so the cut opens the top cleanly; its floor sits at `lift`.
    pocket = Pos(0, 0, lift + (pocket_depth + 1.0) / 2) * Box(pocket_width, pocket_length, pocket_depth + 1.0)
    cup = body - pocket
    if draft:
        return cup

    # Polish the four outer vertical corners only. The pocket is the mating socket, so
    # its mouth and its concave inside edges stay sharp; the rim stays square because a
    # rim chamfer meeting the corner chamfers leaves four sub-1mm2 corner triangles and
    # stops the walls standing full thickness all the way to the rim.
    def outer_corner(edge):
        centre = edge.center()
        return abs(centre.X) > pocket_width / 2 + 1e-3 or abs(centre.Y) > pocket_length / 2 + 1e-3

    corners = cup.edges().filter_by(Axis.Z).filter_by(outer_corner)
    return polish(cup, corners, 1.0)
