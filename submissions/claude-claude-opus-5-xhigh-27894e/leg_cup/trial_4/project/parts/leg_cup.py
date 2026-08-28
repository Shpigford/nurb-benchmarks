from nurb import *


@part
def leg_cup(
    wall_thickness=2.0,
    pocket_depth=8.0,
    leg_clearance=0.4,
    corner_chamfer=1.0,
    draft=False,
):
    """A slip-over cup for the short leg of the workbench.

    The cup sits on the floor, the leg's foot drops into the pocket from above, and
    the solid floor under the foot is what lifts the bench level. Every dimension
    that describes the bench itself comes from `measurements.toml`, so correcting
    the lift there rebuilds the part rather than editing this file.

    wall_thickness: how thick the four walls standing around the leg are
    pocket_depth: how far the leg's foot drops down into the cup
    leg_clearance: total slack across the pocket, so the leg slides on by hand
    corner_chamfer: how much is taken off the four upright corners
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    if lift <= 0:
        reject(
            f"lift is {lift}mm, so there is no floor left under the foot and the cup "
            f"lifts the bench by nothing. Record a lift above 0 in measurements.toml."
        )

    pocket_width = leg_width + leg_clearance
    pocket_breadth = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_breadth = pocket_breadth + 2 * wall_thickness
    height = lift + pocket_depth

    body = Box(outer_width, outer_breadth, height)

    # The cutter overshoots the rim rather than landing on it, so the mouth is opened
    # by a boolean through open air instead of one the kernel has to judge against a
    # coincident face. Its floor is what stays exactly `lift` above the bed.
    overshoot = 1.0
    pocket = Pos(0, 0, height / 2 - pocket_depth / 2 + overshoot / 2) * Box(
        pocket_width, pocket_breadth, pocket_depth + overshoot
    )
    body = body - pocket

    if draft:
        return body

    # Only the four upright corners. The pocket is a socket the leg has to slide into,
    # so nothing inside it is touched, and the rim stays square because the wall has to
    # measure a full `wall_thickness` all the way up to it. An upright corner edge runs
    # in z alone and stands out at both outer faces, which no pocket edge does.
    half_width = outer_width / 2
    half_breadth = outer_breadth / 2
    tol = 1e-6

    def upright_corner(edge):
        box = edge.bounding_box()
        return (
            box.max.Z - box.min.Z > tol
            and box.max.X - box.min.X < tol
            and box.max.Y - box.min.Y < tol
            and abs(abs(box.min.X) - half_width) < tol
            and abs(abs(box.min.Y) - half_breadth) < tol
        )

    corners = body.edges().filter_by(upright_corner)
    return polish(body, corners, corner_chamfer)
