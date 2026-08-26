from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """
    Bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: width across the pole
    """
    clearance = 0.2
    wall = 3.0
    length = 24.0
    axis_height = 18.0

    if pole_diameter < 8.0:
        reject(
            f"pole_diameter {pole_diameter} is under 8mm: raise it to at least 8",
            param="pole_diameter",
        )

    inner_r = pole_diameter / 2.0 + clearance
    floor = axis_height - inner_r
    if floor < 2.0:
        reject(
            f"pole_diameter {pole_diameter} leaves only {floor:.2f}mm of floor under "
            f"an 18mm axis: lower it so the floor is at least 2mm",
            param="pole_diameter",
        )

    half_w = inner_r + wall

    with BuildSketch(Plane.XZ) as sk:
        Rectangle(2 * half_w, axis_height, align=(Align.CENTER, Align.MIN))
        with Locations((0, axis_height)):
            Circle(inner_r, mode=Mode.SUBTRACT)
    body = extrude(sk.sketch, amount=length / 2.0, both=True)

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def _polishable(edge):
        if edge.bounding_box().min.Z <= bed + 0.05:
            return False
        c = edge.bounding_box().center()
        dist = (c.X**2 + (c.Z - axis_height) ** 2) ** 0.5
        return dist > inner_r + 0.4

    keep = body.edges().filter_by(_polishable)
    return polish(body, keep, 1.0)
