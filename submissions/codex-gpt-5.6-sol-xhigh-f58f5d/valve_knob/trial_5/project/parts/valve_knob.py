from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
):
    """A compact replacement knob for a D-shaped valve stem.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if not shaft_diameter / 2.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be between half of shaft_diameter and shaft_diameter",
            param="shaft_across_flat",
        )

    knob_width = 28.0
    knob_height = 16.0
    bore_depth = 12.0
    bore_clearance = 0.7

    # Broad square flats provide grip; only the four vertical outside edges are
    # polished so the bed face and the fit-critical bore remain exact.
    body = Box(
        knob_width,
        knob_width,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = polish(body, body.edges().filter_by(Axis.Z), 1.0)

    # The stem's flat faces +X. Growing both measured dimensions by the same
    # amount leaves 0.35 mm between the measured stem and the bore everywhere.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    flat_x = bore_across_flat - bore_radius
    bore_bottom = knob_height - bore_depth

    round_bore = Cylinder(
        bore_radius,
        bore_depth + 0.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, bore_bottom))
    flat_half_space = Box(
        bore_across_flat,
        bore_diameter * 2.0,
        bore_depth + 0.1,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((-bore_radius, 0.0, bore_bottom))

    bore = round_bore & flat_half_space
    return body - bore
