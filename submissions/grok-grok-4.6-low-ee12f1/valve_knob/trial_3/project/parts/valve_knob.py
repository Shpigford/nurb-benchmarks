from math import cos, sin, radians
from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    height=14.0,
    grip_width=30.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: caliper reading across the round of the stem
    shaft_across_flat: caliper reading from the stem flat to the round side
    height: how tall the knob is, bed to top
    grip_width: narrowest outside width at the waist
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )
    if height < 13.5:
        reject("height must be at least 13.5mm so the stem can seat", param="height")

    clearance = 0.5
    bore_dia = shaft_diameter + clearance
    bore_across = shaft_across_flat + clearance
    bore_r = bore_dia / 2.0
    # Flat faces +X. Across-flat is the round (-X) to the flat.
    flat_x = bore_across - bore_r
    bore_depth = height - 3.5

    hub_r = grip_width / 2.0
    lobe_r = 5.5
    lobe_center = hub_r - 1.5

    body = extrude(Circle(hub_r), height)
    for i in range(4):
        ang = radians(45.0 + i * 90.0)
        body = body + Pos(lobe_center * cos(ang), lobe_center * sin(ang)) * extrude(
            Circle(lobe_r), height
        )

    d_circle = Circle(bore_r)
    slab = Pos(flat_x + 20.0, 0) * Rectangle(40.0, 40.0)
    d_profile = d_circle - slab
    bore = Pos(0, 0, height - bore_depth) * extrude(d_profile, bore_depth + 2.0)
    body = body - bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = keep.filter_by(
        lambda e: (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 > bore_r + 0.4
    )
    return polish(body, keep, 1.0)
