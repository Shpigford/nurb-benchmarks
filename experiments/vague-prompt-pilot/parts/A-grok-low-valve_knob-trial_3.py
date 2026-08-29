from nurb import *
from math import cos, radians, sin


@part
def valve_knob(
    knob_diameter=46.0,
    knob_height=22.0,
    push_clearance=0.30,
    grip_scallops=8,
    scallop_width=12.0,
    draft=False,
):
    """Replacement hose-valve knob for a D-shaft stem.

    knob_diameter: overall width of the grip
    knob_height: how tall the knob prints, including the solid cap
    push_clearance: extra on the D-bore versus the measured stem, so it pushes on snug
    grip_scallops: number of finger cups around the rim
    scallop_width: how wide each finger cup is
    """
    shaft_dia = measured("shaft_diameter")
    across_flat = measured("shaft_across_flat")
    stem = measured("stem_stickout")

    if push_clearance < 0.1:
        reject(
            "push_clearance under 0.1mm will need a hammer; raise it to 0.2 or more",
            param="push_clearance",
        )
    if push_clearance > 0.6:
        reject(
            "push_clearance over 0.6mm will rattle and may spin on the stem; drop it to 0.3",
            param="push_clearance",
        )

    floor = 5.0
    bore_depth = stem + 0.5
    if knob_height < bore_depth + floor:
        reject(
            f"knob_height {knob_height} is too short for a {bore_depth}mm bore plus a {floor}mm cap; raise it above {bore_depth + floor}",
            param="knob_height",
        )
    if knob_diameter < shaft_dia + 16.0:
        reject(
            f"knob_diameter {knob_diameter} leaves less than 8mm of rim around the stem; raise it above {shaft_dia + 16.0}",
            param="knob_diameter",
        )
    if grip_scallops < 4:
        reject("need at least 4 grip scallops to hold with wet hands", param="grip_scallops")

    body = Cylinder(knob_diameter / 2, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    scallop_r = scallop_width / 2
    ring = knob_diameter / 2 - 1.5
    for i in range(grip_scallops):
        ang = radians(i * 360.0 / grip_scallops)
        cup = Cylinder(
            scallop_r, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        ).locate(Location((ring * cos(ang), ring * sin(ang), 0)))
        body = body - cup

    bore_r = (shaft_dia + push_clearance) / 2
    # Flat faces +X. Across-flat is from the round (-X) to the flat.
    flat_x = -bore_r + (across_flat + push_clearance)
    d_profile = Circle(bore_r) - Pos(flat_x + 20.0, 0) * Rectangle(40.0, 40.0)
    # Bore opens at the top (+Z) on the vertical centreline.
    bore = extrude(d_profile, amount=bore_depth).locate(
        Location((0, 0, knob_height - bore_depth))
    )
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    sharp = concave_edges(body)
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = ShapeList(e for e in keep if e not in sharp)
    return polish(body, keep, 1.0)
