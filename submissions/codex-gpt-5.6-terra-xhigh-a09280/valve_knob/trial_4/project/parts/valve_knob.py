from nurb import *


@part
def valve_knob(
    shaft_diameter: float = 8.0,
    shaft_across_flat: float = 6.5,
    knob_height: float = 16.0,
    bore_clearance: float = 0.8,
    core_radius: float = 15.0,
    lobe_radius: float = 5.5,
    lobe_offset: float = 13.5,
    draft: bool = False,
):
    """A four-lobed replacement handle for a D-profile valve stem.

    shaft_diameter: diameter across the stem's round sides.
    shaft_across_flat: distance from the stem flat to its opposite round side.
    knob_height: total printed height of the knob.
    bore_clearance: total diametral and flat-to-round clearance in the D bore.
    core_radius: radius of the round center that keeps the knob comfortable in hand.
    lobe_radius: radius of each rounded grip lobe.
    lobe_offset: distance from the center to each grip lobe.
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be positive", param="shaft_diameter")
    if not 0.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be positive and smaller than shaft_diameter",
            param="shaft_across_flat",
        )
    if knob_height < 12.0:
        reject("knob_height must be at least 12.0mm", param="knob_height")

    # The bore is deliberately a D rather than a circular hole.  Its straight face
    # is at +X while printed, matching the orientation of the measured valve stem.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_depth = min(12.0, knob_height - 3.0)
    # Cylinders are centered in all three axes.  The socket's upper rim is flush
    # with the knob top, leaving a 4mm floor for the measured 12mm proud stem.
    bore_center_z = knob_height / 2.0 - bore_depth / 2.0

    body = Cylinder(core_radius, knob_height)
    for x, y in ((lobe_offset, 0.0), (-lobe_offset, 0.0), (0.0, lobe_offset), (0.0, -lobe_offset)):
        body = body + Cylinder(lobe_radius, knob_height).translate((x, y, 0.0))

    bore_circle = Cylinder(bore_radius, bore_depth).translate((0.0, 0.0, bore_center_z))
    # Remove the positive-X cap of the circle to make the bore's D flat.
    flat_cap = Box(
        bore_diameter * 2.0,
        bore_diameter * 2.0,
        bore_depth,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    ).translate((bore_flat_x, 0.0, bore_center_z))
    d_bore = bore_circle - flat_cap

    return body - d_bore
