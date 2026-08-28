from nurb import *


# Keep the measured defaults as floats in the part signature, so this remains a
# configurable part rather than a one-off model of this particular stem.
DEFAULT_SHAFT_DIAMETER = measured("shaft_diameter")
DEFAULT_SHAFT_ACROSS_FLAT = measured("shaft_across_flat")


@part
def valve_knob(
    shaft_diameter=DEFAULT_SHAFT_DIAMETER,
    shaft_across_flat=DEFAULT_SHAFT_ACROSS_FLAT,
    knob_height=15.0,
    fit_clearance=0.7,
    draft=False,
):
    """Three-lobed replacement knob for a D-shaped valve stem.

    shaft_diameter: diameter measured across the round side of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    knob_height: overall printed height, including the solid floor below the bore
    fit_clearance: diametral and across-flat clearance built into the D-shaped bore
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be positive", param="shaft_diameter")
    if shaft_across_flat <= 0.0 or shaft_across_flat > shaft_diameter:
        reject(
            "shaft_across_flat must be positive and no larger than shaft_diameter",
            param="shaft_across_flat",
        )
    if knob_height < 15.0:
        reject("knob_height must stay at least 15mm for the 12mm-deep stem bore", param="knob_height")
    if fit_clearance < 0.4:
        reject("fit_clearance must be at least 0.4mm for a printed valve-stem fit", param="fit_clearance")

    # A 12mm deep blind bore accepts the proud stem while retaining a 3mm floor.
    bore_depth = 12.0
    bore_diameter = shaft_diameter + fit_clearance
    bore_radius = bore_diameter / 2.0
    bore_across_flat = shaft_across_flat + fit_clearance

    # For a D with its flat facing +X, the flat is this far right of the axis.
    bore_flat_x = bore_across_flat - bore_radius

    # The 15mm core guarantees a 30mm minimum hand span. Three 7mm lobes at
    # 13mm radius reach 20mm from center, giving wet hands a positive grip.
    body = Cylinder(15.0, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in ((13.0, 0.0), (-6.5, 11.26), (-6.5, -11.26)):
        body += Pos(x, y) * Cylinder(7.0, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Intersect a round bore with a box ending at the flat plane. The box retains
    # x <= bore_flat_x, so the mating stem's flat faces +X exactly as installed.
    round_bore = Pos(0.0, 0.0, knob_height) * Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MAX),
    )
    flat_bore_limit = Pos(bore_flat_x, 0.0, knob_height) * Box(
        bore_radius + bore_flat_x,
        bore_diameter,
        bore_depth,
        align=(Align.MAX, Align.CENTER, Align.MAX),
    )
    d_bore = round_bore & flat_bore_limit
    return body - d_bore
