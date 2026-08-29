from math import cos, radians, sin

from nurb import *

FLOOR = 4.0
STEM_SLACK = 1.0
SCALLOP_DIA = 10.0
SCALLOP_RING = 19.5
LEAD_IN = 1.0


@part
def valve_knob(
    bore_clearance=0.2,
    flat_clearance=0.15,
    stem_length=12.0,
    knob_diameter=35.0,
    scallop_count=7,
    draft=False,
):
    """Replacement knob for a hose-valve D-shaft.

    bore_clearance: extra bore width for push fit; raise if tight, lower if it rattles
    flat_clearance: extra room at the D-flat; raise if tight, lower if it rattles
    stem_length: how far the stem sticks out of the valve body
    knob_diameter: overall knob size
    scallop_count: finger scallops around the rim
    """
    bore_depth = stem_length + STEM_SLACK
    knob_height = bore_depth + FLOOR
    shaft_diameter = measured("shaft_diameter")
    shaft_across_flat = measured("shaft_across_flat")
    bore_dia = shaft_diameter + bore_clearance
    bore_r = bore_dia / 2
    flat_x = (shaft_across_flat + flat_clearance) - bore_r
    n_scallops = max(3, int(round(scallop_count)))

    body = Cylinder(knob_diameter / 2, knob_height)
    body = body.move(Location((0, 0, knob_height / 2)))

    for i in range(n_scallops):
        a = radians(i * 360.0 / n_scallops)
        loc = Location((SCALLOP_RING * cos(a), SCALLOP_RING * sin(a), knob_height / 2))
        body -= Cylinder(SCALLOP_DIA / 2, knob_height + 0.4).move(loc)

    if draft:
        return body

    bore = Cylinder(bore_r, bore_depth + 0.2)
    bore = bore.move(Location((0, 0, FLOOR + (bore_depth + 0.2) / 2)))
    clip = Box(20, 20, bore_depth + 2)
    clip = clip.move(Location((flat_x + 10, 0, FLOOR + bore_depth / 2)))
    body -= bore - clip

    top = knob_height
    inner_top = body.edges().filter_by(
        lambda e: abs(e.center().Z - top) < 0.05
        and e.center().X ** 2 + e.center().Y ** 2 < (bore_r + 1.5) ** 2
    )
    if inner_top:
        body = chamfer(inner_top, LEAD_IN)

    bed = body.bounding_box().min.Z
    bed_outer = body.edges().filter_by(
        lambda e: abs(e.bounding_box().max.Z - bed) < 0.08
        and abs(e.bounding_box().min.Z - bed) < 0.08
        and (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 > knob_diameter / 2 - 3
    )
    if bed_outer:
        body = chamfer(bed_outer, 0.5)

    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.2)
    keep = ShapeList(e for e in keep if e not in concave_edges(body))
    return polish(body, keep, 1.0)
