from nurb import *


@part
def pole_rest(rest_length=12.0, wall=3.0, draft=False):
    """Bench rest for a finishing pole or dowel, open at the top so the pole drops in.

    rest_length: how far along the pole this rest is
    wall: plastic beside the cradle and under it
    """
    pole = measured("pole_diameter")
    center_z = measured("pole_center_height")
    radius = pole / 2.0

    if wall < 2.0:
        reject("wall under 2mm prints weak; raise wall to 2 or more", param="wall")
    if rest_length < 8.0:
        reject(
            "rest_length under 8mm is too short to cradle; raise it to 8 or more",
            param="rest_length",
        )

    under = center_z - radius
    if under < wall:
        reject(
            f"only {under:.1f}mm under the cradle at this pole and center height; "
            f"raise wall is not possible here — the rest needs at least {wall}mm of floor",
            param="wall",
        )

    # Top of the block sits at the pole center so the cradle is a semicircle:
    # opening equals pole diameter, drop-in from above, no tunnel to thread through.
    width = pole + 2.0 * wall
    height = center_z

    body = Pos(0, 0, height / 2.0) * Box(width, rest_length, height)
    cradle = Pos(0, 0, center_z) * Rot(90, 0, 0) * Cylinder(radius, rest_length + 4.0)
    rest = body - cradle

    if draft:
        return rest
    bed = rest.bounding_box().min.Z
    keep = rest.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    keep = keep - rest.edges().filter_by(GeomType.CIRCLE)
    return polish(rest, keep, 1.0)
