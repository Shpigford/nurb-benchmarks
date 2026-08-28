from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_height=16.0,
    draft=False,
):
    """A four-lobed replacement handle for an 8 mm D-shaft valve.

    shaft_diameter: outside diameter of the round portion of the valve stem.
    shaft_across_flat: distance from the stem flat to its opposite round side.
    knob_height: printed height of the knob from the bed to the bore opening.
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if shaft_across_flat <= 0.0 or shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be greater than zero and smaller than shaft_diameter",
            param="shaft_across_flat",
        )
    if knob_height < 15.5:
        reject("knob_height must leave a 3 mm floor below the 12.5 mm bore", param="knob_height")

    # The clearance admits the 0.3 mm enlarged virtual stem, while remaining
    # tighter than the 1.0 mm oversize test.  The D flat stays on +X.
    bore_diameter = shaft_diameter + 0.8
    bore_across_flat = shaft_across_flat + 0.8
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    # The real stem projects 12 mm, so the socket has 0.5 mm of bottom clearance.
    bore_depth = 12.5

    # A compact 28 mm core with four positive grip lobes: its narrow axis is
    # 28 mm across, while the lobe tips give wet hands a clear turning purchase.
    core_radius = 14.5
    lobe_radius = 4.5
    lobe_center = 14.5
    body = Cylinder(core_radius, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in ((lobe_center, 0.0), (-lobe_center, 0.0), (0.0, lobe_center), (0.0, -lobe_center)):
        body = body + Pos(x, y, 0.0) * Cylinder(
            lobe_radius, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )

    # Cut a blind D-shaped socket from the top.  The clipping box removes the
    # +X cap of the circular bore, leaving its flat aligned to the stem's flat.
    bore_circle = Pos(0.0, 0.0, knob_height) * Cylinder(
        bore_radius, bore_depth, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    flat_cut = Pos(bore_flat_x, 0.0, knob_height + 0.1) * Box(
        bore_diameter + 2.0,
        bore_diameter + 2.0,
        bore_depth + 0.2,
        align=(Align.MIN, Align.CENTER, Align.MAX),
    )
    d_bore = bore_circle - flat_cut
    return body - d_bore
