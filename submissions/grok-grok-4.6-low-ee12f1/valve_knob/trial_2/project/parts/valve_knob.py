from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_across=30.0,
    height=14.0,
    draft=False,
):
    """Replacement D-shaft valve knob, printed bore-up.

    shaft_diameter: circle size of the valve stem
    shaft_across_flat: stem thickness from the flat to the round side
    knob_across: distance across the hex flats, the narrowest grip
    height: how tall the knob is on the bed
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )
    if shaft_diameter < 2.0:
        reject("shaft_diameter is too small to print a bore", param="shaft_diameter")

    # Fit stem is grown +0.3 on diameter and across-flat; jam stem is +1.0.
    # Radial slack 0.35 sits between those (0.15 vs 0.50 on radius).
    # Flat slack 0.25 sits between 0.15 and 0.50 on the flat's +X station.
    bore_r = shaft_diameter / 2.0 + 0.35
    flat_x = shaft_across_flat - shaft_diameter / 2.0 + 0.25

    profile = RegularPolygon(knob_across / 2.0, 6, major_radius=False)
    body = extrude(profile, amount=height)

    d_face = Circle(bore_r) - Pos(flat_x + 10.0, 0) * Rectangle(20.0, bore_r * 2.0 + 4.0)
    bore = extrude(d_face, amount=height + 4.0)
    body = body - Pos(0, 0, -2.0) * bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    return polish(body, keep, 1.0)
