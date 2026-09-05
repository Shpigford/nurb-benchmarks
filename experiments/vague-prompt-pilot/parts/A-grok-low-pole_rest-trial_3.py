from nurb import *


@part
def pole_rest(
    rest_length=10.0,
    wall=3.0,
    center_height=18.0,
    draft=False,
):
    """Open cradle for a wet-finished pole or dowel, printed as it sits on the bench.

    rest_length: how long the cradle is along the pole
    wall: thickness of the foot and the cradle sides
    center_height: how high the pole axis sits above the bench
    """
    pole_d = measured("pole_diameter")
    pole_r = pole_d / 2.0
    if wall < 2.0:
        reject(
            f"wall {wall} is under 2mm and will print as a smear; raise it",
            param="wall",
        )
    if rest_length < 6.0:
        reject(
            f"rest_length {rest_length} is too short to sit stably; raise it above 6",
            param="rest_length",
        )
    floor = center_height - pole_r
    if floor < wall:
        reject(
            f"center_height {center_height} leaves only {floor:.1f}mm under a "
            f"{pole_d}mm pole; raise center_height or lower wall",
            param="center_height",
        )

    # Foot on the bench, walls stop at the equator so the pole drops in from above.
    foot_width = 2.0 * (pole_r + wall) + 4.0
    height = center_height
    body = Box(foot_width, rest_length, height)
    body = body.move(Location((0, 0, height / 2.0)))

    groove = Cylinder(pole_r, rest_length + 4.0)
    groove = groove.rotate(Axis.X, 90.0)
    groove = groove.move(Location((0, 0, center_height)))
    body = body - groove

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def on_cradle(edge):
        c = edge.bounding_box().center()
        radial = ((c.X) ** 2 + (c.Z - center_height) ** 2) ** 0.5
        return abs(radial - pole_r) < 0.4

    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = ShapeList(e for e in keep if not on_cradle(e))
    return polish(body, keep, 1.0)
