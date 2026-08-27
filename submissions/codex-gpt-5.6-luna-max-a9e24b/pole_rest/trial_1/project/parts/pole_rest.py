from nurb import *


@part
def pole_rest(pole_diameter: float = measured("pole_diameter")):
    """
    A support-free cradle for a freshly finished pole drying across the Y axis.

    pole_diameter: diameter of the pole this rest cradles
    """
    pole_radius = pole_diameter / 2.0
    pole_clearance = 0.10
    cavity_radius = pole_radius + pole_clearance

    rest_length = 28.0
    body_height = 16.0
    side_backing = 2.4
    outer_width = 2.0 * (cavity_radius + side_backing)

    body = Box(
        outer_width,
        rest_length,
        body_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # The cutter is concentric with the pole axis: X=0, Z=18, and runs through
    # the full Y span.  The body top stays below the pole centre so the pole can
    # be lowered vertically into the open seat.
    cavity = Cylinder(
        cavity_radius,
        rest_length + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    cavity = Pos(0, 0, 18.0) * Rot(90, 0, 0) * cavity
    cradle = body - cavity

    if draft:
        return cradle

    # Keep the functional inner cradle and bed face sharp; polish only the
    # remaining exposed edges when the kernel can land the chamfer cleanly.
    bed = cradle.bounding_box().min.Z
    exposed = cradle.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > bed + 0.01
    )
    return polish(cradle, exposed, 1.0)
