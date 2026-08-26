from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_width=32.0,
    height=15.0,
    draft=False,
):
    """Replacement handle for a valve D-stem, printed bore-up.

    shaft_diameter: round-side diameter of the valve stem
    shaft_across_flat: stem thickness from the flat to the opposite round
    knob_width: distance across the hex flats, the grip
    height: overall printed height
    """
    if shaft_diameter < 4.0:
        reject(
            "shaft_diameter is under 4mm: a printed bore that small will close up",
            param="shaft_diameter",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter to form a D",
            param="shaft_across_flat",
        )
    if shaft_across_flat < 2.0:
        reject(
            "shaft_across_flat is under 2mm: the bore cannot print",
            param="shaft_across_flat",
        )

    # Modelled clearance: larger than the 0.3mm virtual stem, tighter than 1.0mm.
    clearance = 0.5
    bore_r = (shaft_diameter + clearance) / 2.0
    bore_across = shaft_across_flat + clearance
    flat_x = bore_across - bore_r
    floor = 3.0
    if height - floor < 10.2:
        reject(
            "height is too short for 10mm of stem engagement plus a 3mm floor",
            param="height",
        )
    if knob_width < 2.0 * bore_r + 6.0:
        reject(
            "knob_width leaves under 3mm of wall around the bore",
            param="knob_width",
        )

    body = extrude(
        RegularPolygon(knob_width / 2.0, 6, major_radius=False),
        height,
    )

    # D-bore opens at the top, flat facing +X. Extra length breaks the top face.
    d_profile = Circle(bore_r) - Pos(flat_x + bore_r, 0) * Rectangle(
        bore_r * 2.0, bore_r * 4.0
    )
    cutter = Pos(0, 0, floor) * extrude(d_profile, height - floor + 1.0)
    body = body - cutter

    if draft:
        return body

    # Polish the outer top rim only. Bore, floor and bed stay sharp for fit and grip.
    top_z = body.bounding_box().max.Z
    keep = body.edges().filter_by(lambda e: abs(e.center().Z - top_z) < 0.2)
    keep = keep.filter_by(
        lambda e: (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 > bore_r + 1.0
    )
    return polish(body, keep, 1.0)
