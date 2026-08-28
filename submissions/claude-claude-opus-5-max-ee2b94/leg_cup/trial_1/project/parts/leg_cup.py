from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """A slip-over foot cup: the short bench leg drops in and the solid floor lifts it level.

    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far down the leg's foot sits inside the cup
    leg_clearance: extra room around the leg so the cup slips on by hand
    """
    lift = measured("lift")
    if lift < 1.2:
        # Three beads is the thinnest floor that prints as a floor rather than a skin,
        # and this floor is the whole point of the part: it carries the bench.
        reject(
            f"lift {lift} leaves a floor thinner than 1.2mm, which prints as a skin and "
            f"crushes under the bench. Raise lift in measurements.toml above 1.2",
            param="lift",
        )

    # The mouth mirrors the leg's own two measurements; pocket_depth is the vertical.
    mouth_width = measured("leg_width") + leg_clearance
    mouth_depth = measured("leg_depth") + leg_clearance
    width = mouth_width + 2 * wall_thickness
    depth = mouth_depth + 2 * wall_thickness
    height = lift + pocket_depth

    base = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(width, depth, height, align=base)

    # Cut the pocket from above, overshooting the rim so the mouth is a clean opening
    # rather than two coincident faces for the kernel to argue about.
    over = 1.0
    pocket = Pos(0, 0, lift) * Box(
        mouth_width, mouth_depth, pocket_depth + over, align=base
    )
    cup = body - pocket

    if draft:
        return cup

    # Keep the pocket sharp: it is the mating mouth the leg slides into, and a lead-in
    # chamfer there is the polish rule's named mistake. Keep the bed face sharp too, and
    # keep the top rim, so the wall stays a full 2mm of bearing surface all the way up
    # and three chamfers never meet at a corner. What is left is the four vertical
    # corners, which are the edges a hand actually meets.
    bed = cup.bounding_box().min.Z
    rim = cup.bounding_box().max.Z
    inside = concave_edges(cup)

    def handled(edge):
        box = edge.bounding_box()
        if edge in inside:
            return False
        if box.max.Z <= bed + 0.01 or box.min.Z >= rim - 0.01:
            return False  # lies in the bed face or in the rim face
        # Wholly within the pocket's plan outline: the mouth and the pocket walls.
        # Reach is measured from the centreline, so a corner at -13.2 counts as far
        # out as one at +13.2; comparing a bare max against a half-width silently
        # keeps the two corners on the negative side and drops the other two.
        reach_x = max(abs(box.min.X), abs(box.max.X))
        reach_y = max(abs(box.min.Y), abs(box.max.Y))
        return not (
            reach_x <= mouth_width / 2 + 0.01
            and reach_y <= mouth_depth / 2 + 0.01
        )

    return polish(cup, cup.edges().filter_by(handled), 1.0)
