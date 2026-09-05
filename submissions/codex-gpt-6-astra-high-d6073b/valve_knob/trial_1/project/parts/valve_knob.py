from nurb import *


@part
def valve_knob(
    shaft_diameter: float = float(measured("shaft_diameter")),
    shaft_across_flat: float = float(measured("shaft_across_flat")),
    grip_length: float = 40.0,
    grip_width: float = 30.0,
    knob_height: float = 14.0,
    draft=False,
):
    """Oval valve knob, printed with its blind D socket facing upward.

    shaft_diameter: measured diameter of the stem's circular portion.
    shaft_across_flat: distance from the stem's flat to its opposite round side.
    grip_length: overall length of the oval hand grip.
    grip_width: overall width of the oval hand grip.
    knob_height: height from the flat print bed face to the socket mouth.
    """
    if not shaft_diameter / 2 < shaft_across_flat < shaft_diameter:
        reject("The flat distance must lie between half and all of the shaft diameter.",
               param="shaft_across_flat")
    if knob_height < 14.0:
        reject("Use at least 14mm height for an 11mm socket and 3mm floor.",
               param="knob_height")
    if min(grip_width, grip_length) < shaft_diameter + 10.0:
        reject("The grip must be at least 10mm wider than the shaft.", param="grip_width")

    body = extrude(Ellipse(grip_length / 2, grip_width / 2), amount=knob_height)
    if not draft:
        # Only the exposed outer top rim: preserve the bed and every mating edge.
        top_rim = body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > knob_height - 0.001
        )
        body = polish(body, top_rim, 1.0)

    # Across-flat is measured from -radius to the +X chord, not from the axis.
    # Adding 0.5 to both measured spans clears the +0.3 test stem while
    # retaining the chord that steers the valve and excludes the +1.0 stem.
    bore_radius = (shaft_diameter + 0.5) / 2
    flat_x = shaft_across_flat + 0.5 - bore_radius
    socket_depth = 11.0
    socket_bottom = knob_height - socket_depth
    circular_cut = Pos(0, 0, socket_bottom) * Cylinder(
        bore_radius, socket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    flat_limit = Pos(-bore_radius - 1.0, -bore_radius - 1.0, socket_bottom) * Box(
        flat_x + bore_radius + 1.0,
        2 * bore_radius + 2.0,
        socket_depth + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    return body - (circular_cut & flat_limit)
