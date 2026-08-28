from nurb import *


@part
def leg_cup(
    wall_thickness=2.0,
    pocket_depth=8.0,
    leg_clearance=0.4,
    chamfer_size=1.2,
    draft=False,
):
    """A slip-over cup for the short bench leg: the foot drops in, the solid floor lifts it level.

    wall_thickness: how thick the four side walls around the leg are
    pocket_depth: how far the leg's foot drops down into the cup
    leg_clearance: extra room around the leg so the cup slips on by hand
    chamfer_size: how big a flat is taken off the outside edges
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")
    if lift <= 0:
        reject("lift is the floor under the foot: at zero there is no floor and no cup")

    pocket_width = leg_width + leg_clearance
    pocket_depth_y = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_depth = pocket_depth_y + 2 * wall_thickness
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(outer_width, outer_depth, height)
    # The pocket runs out through the top so nothing roofs it over.
    mouth = Pos(0, 0, lift + (pocket_depth + 1.0) / 2) * Box(
        pocket_width, pocket_depth_y, pocket_depth + 1.0
    )
    body = body - mouth

    if draft:
        return body

    # The four outside corners, and nothing else. The rim stays sharp: on a 2mm wall
    # there is no chamfer size that both clears the sliver floor at the top corners and
    # leaves a lip worth calling a wall. Edges lying in the bottom face are the bed, and
    # the pocket mouth is fit geometry.
    tol = 1e-6

    def outer_corner(edge):
        b = edge.bounding_box()
        return (
            b.max.Z - b.min.Z > height - tol
            and (b.max.X > outer_width / 2 - tol or b.min.X < -outer_width / 2 + tol)
            and (b.max.Y > outer_depth / 2 - tol or b.min.Y < -outer_depth / 2 + tol)
        )

    return polish(body, body.edges().filter_by(outer_corner), chamfer_size)
