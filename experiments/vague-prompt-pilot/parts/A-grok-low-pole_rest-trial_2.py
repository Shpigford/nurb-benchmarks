from nurb import *


@part
def pole_rest(
    rest_length=12.0,
    wall=3.0,
    center_height=18.0,
    draft=False,
):
    """Bench rest that cradles a drying pole so its center matches the rest of the row.

    rest_length: how far the rest runs along the pole
    wall: thickness beside the cradle
    center_height: how high the pole's center sits above the bench
    """
    pole_d = measured("pole_diameter")
    radius = pole_d / 2.0
    min_height = radius + wall
    if center_height < min_height:
        reject(
            f"center_height {center_height} leaves less than {wall}mm under the cradle; raise it to {min_height} or more",
            param="center_height",
        )
    if rest_length < 8.0:
        reject(
            "rest_length under 8mm is too short to sit stably; raise it",
            param="rest_length",
        )
    if wall < 2.0:
        reject(
            "wall under 2mm is too thin to print; raise it",
            param="wall",
        )

    width = pole_d + 2.0 * wall
    height = center_height

    body = Box(width, rest_length, height).moved(Location((0, 0, height / 2.0)))
    cradle = Cylinder(radius, rest_length + 4.0)
    cradle = cradle.rotate(Axis.X, 90.0).moved(Location((0, 0, center_height)))
    body = body - cradle

    if draft:
        return body
    bed = body.bounding_box().min.Z
    # Leave the cradle and its rims sharp so polish cannot nick the seat or leave slivers
    # where the trough meets the top.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05
        and abs(e.center().X) > radius + 0.5
    )
    return polish(body, keep, 1.0)
