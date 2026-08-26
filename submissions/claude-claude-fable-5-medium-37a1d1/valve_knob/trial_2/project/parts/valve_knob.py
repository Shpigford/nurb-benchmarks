from nurb import *
import math


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    bore_clearance=0.6,
    knob_height=14.0,
    core_width=29.0,
    lobe_count=5,
    lobe_width=8.0,
    lobe_reach=17.5,
    draft=False,
):
    """Replacement valve knob, printed bore-up and flipped onto the D-stem.

    shaft_diameter: the round measurement of the valve stem
    shaft_across_flat: stem measured from the flat to the round side
    bore_clearance: total extra on the bore over the stem, so it slides on without rattle
    knob_height: overall height of the knob
    core_width: width of the round body between the lobes
    lobe_count: how many finger lobes ring the body
    lobe_width: how fat each lobe is
    lobe_reach: how far the tip of each lobe sits from the centre
    """
    bore_depth = knob_height - 3.0
    if bore_depth < 10.5:
        reject("knob_height leaves the bore under 10.5mm deep: raise it above 13.5", param="knob_height")
    if core_width / 2 >= lobe_reach:
        reject("lobe_reach must sit past the core: raise it above %.1f" % (core_width / 2), param="lobe_reach")

    body = Cylinder(core_width / 2, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lobe_centre = lobe_reach - lobe_width / 2
    for i in range(lobe_count):
        a = 2 * math.pi * i / lobe_count
        lobe = Cylinder(lobe_width / 2, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = body + lobe.moved(Location((lobe_centre * math.cos(a), lobe_centre * math.sin(a), 0)))

    # D-bore: stem circle plus clearance, flat facing +X, opening at the top.
    r = (shaft_diameter + bore_clearance) / 2
    flat_x = (shaft_across_flat + bore_clearance) - r
    circle = Circle(r)
    cutter = Rectangle(2 * r, 2 * r, align=(Align.MIN, Align.CENTER)).moved(Location((flat_x, 0)))
    d_profile = circle - cutter
    bore = extrude(d_profile, bore_depth).moved(Location((0, 0, knob_height - bore_depth)))
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and not any(e.is_same(c) for c in concave)
    )
    return polish(body, keep, 1.0)
