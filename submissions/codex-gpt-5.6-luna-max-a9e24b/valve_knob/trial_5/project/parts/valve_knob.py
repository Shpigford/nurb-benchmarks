"""Parametric replacement knob for the measured D-shaped valve stem."""

from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A support-free, six-lobed valve knob printed with its bore facing up.

    shaft_diameter: measured round diameter of the valve stem
    shaft_across_flat: measured width to the stem's +X-facing flat
    """
    if shaft_diameter <= 0:
        reject("shaft_diameter must be greater than 0mm", param="shaft_diameter")
    if shaft_across_flat <= 0 or shaft_across_flat > shaft_diameter:
        reject(
            "shaft_across_flat must be between 0 and shaft_diameter",
            param="shaft_across_flat",
        )

    # A 0.25mm radial/linear allowance leaves the +0.3mm test stem a small
    # running fit while retaining a positive keying land for torque transfer.
    bore_radius = shaft_diameter / 2.0 + 0.25
    bore_flat_x = shaft_across_flat / 2.0 + 0.25

    knob_height = 15.0
    bore_depth = 11.0
    bore_floor_z = knob_height - bore_depth

    # The central disk guarantees a 28mm minimum grip diameter. Six overlapping
    # round lobes add a little over 12% more reach without filling the entire
    # 36mm envelope.
    body = Cylinder(
        radius=14.2,
        height=knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for angle in range(0, 360, 60):
        lobe_center = 14.8
        x = lobe_center * cos(radians(angle))
        y = lobe_center * sin(radians(angle))
        body += Pos(x, y, 0) * Cylinder(
            radius=2.8,
            height=knob_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Form a true D-shaped negative: a circular bore clipped by a plane whose
    # normal is +X. The small oversize is derived from both measured dimensions.
    round_bore = Pos(0, 0, bore_floor_z) * Cylinder(
        radius=bore_radius,
        height=bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    flat_halfspace = Pos(
        -bore_radius - 1.0,
        -bore_radius - 1.0,
        bore_floor_z,
    ) * Box(
        bore_radius + bore_flat_x + 1.0,
        2.0 * bore_radius + 2.0,
        bore_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    d_bore = round_bore & flat_halfspace

    result = body - d_bore
    return result
