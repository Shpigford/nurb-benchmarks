from nurb import *


@part
def valve_knob(
    shaft_diameter: float = measured("shaft_diameter"),
    shaft_across_flat: float = measured("shaft_across_flat"),
):
    """A compact square-grip replacement knob for a vertical D-shaft.

    shaft_diameter: the measured diameter across the shaft's round section.
    shaft_across_flat: distance from the shaft's flat to its opposite round side.
    """
    knob_width = 30.0
    knob_height = 14.0
    bore_depth = 12.0
    radial_clearance = 0.4

    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if shaft_across_flat <= shaft_diameter / 2.0 or shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must fall between half and all of shaft_diameter for a D-shaft",
            param="shaft_across_flat",
        )

    # The bore is deliberately derived from both measurements.  Its flat faces +X.
    bore_radius = shaft_diameter / 2.0 + radial_clearance
    bore_across_flat = shaft_across_flat + 2.0 * radial_clearance
    flat_x = bore_across_flat - bore_radius
    bore_bottom = knob_height - bore_depth

    body = Box(
        knob_width,
        knob_width,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    round_bore = Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, bore_bottom))
    flat_cut = Box(
        bore_radius + 2.0,
        2.0 * bore_radius + 2.0,
        bore_depth,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((flat_x, 0.0, bore_bottom))

    d_bore = round_bore - flat_cut
    return body - d_bore
