from nurb import *


@part
def pole_rest(pole_diameter=20.0, draft=False):
    """A drop-in drying rest for a freshly finished pole.

    pole_diameter: diameter of the pole being dried
    """
    pole_radius = pole_diameter / 2.0
    fit_clearance = 0.1
    inner_radius = pole_radius + fit_clearance

    rest_length = 22.0
    body_width = 29.0
    body_top = 18.0
    pole_axis_height = 18.0

    body = Box(
        body_width,
        rest_length,
        body_top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # A through-Y cylindrical void leaves a continuous, 180-degree lower cradle.
    # The bore is 0.1 mm larger in radius than the pole, so the pole drops in
    # vertically without touching while the surrounding material backs the seat.
    bore_length = rest_length + 2.0
    pole_bore = (
        Pos(0, bore_length / 2.0, pole_axis_height)
        * Rot(90, 0, 0)
        * Cylinder(
            inner_radius,
            bore_length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    rest = body - pole_bore

    if draft:
        return rest

    bed = rest.bounding_box().min.Z
    exposed_edges = rest.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > bed + 1e-6
        and (
            edge.bounding_box().min.X < -body_width / 2.0 + 1e-6
            or edge.bounding_box().max.X > body_width / 2.0 - 1e-6
        )
    )
    return polish(rest, exposed_edges, 1.0)
