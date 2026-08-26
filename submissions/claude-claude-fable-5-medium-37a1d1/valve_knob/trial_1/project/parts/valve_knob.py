from nurb import *
import math


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_width=28.0,
    knob_height=15.0,
    bore_clearance=0.4,
    floor_thickness=3.0,
    draft=False,
):
    """A six-sided replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: the round width of the valve stem
    shaft_across_flat: the stem measured from its flat to the round side
    knob_width: the knob measured across its flats, what the hand grips
    knob_height: how tall the knob stands
    bore_clearance: extra room in the bore over the stem, total on each dimension
    floor_thickness: material left under the stem at the top of the knob
    """
    bore_dia = shaft_diameter + bore_clearance
    bore_flat = shaft_across_flat + bore_clearance
    bore_depth = knob_height - floor_thickness
    if bore_depth < 10.5:
        reject(
            f"knob_height {knob_height} leaves a {bore_depth:.1f}mm bore; "
            f"the stem needs 10mm plus the floor, so raise it above {floor_thickness + 10.5}",
            param="knob_height",
        )
    if knob_width < bore_dia + 6.0:
        reject(
            f"knob_width {knob_width} leaves under 3mm of wall around the {bore_dia:.1f}mm bore",
            param="knob_width",
        )
    if bore_flat >= bore_dia:
        reject("shaft_across_flat must be less than shaft_diameter", param="shaft_across_flat")

    # Hexagonal grip: inradius is half the width, corners reach 15% further.
    body = extrude(RegularPolygon(knob_width / 2, 6, major_radius=False), knob_height)

    # D-bore: a cylinder with a flat cut on the +X side, opening through the top.
    bore = Pos(0, 0, knob_height - bore_depth) * Cylinder(
        bore_dia / 2, bore_depth, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    flat_x = bore_flat - bore_dia / 2  # flat sits this far from the centerline, toward +X
    trim = Pos(flat_x + bore_dia / 2, 0, knob_height - bore_depth) * Box(
        bore_dia, bore_dia + 1, bore_depth, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    bore = bore - trim
    body = body - bore
    if draft:
        return body
    bed = body.bounding_box().min.Z
    # Only the outer hex edges get chamfered; the bore keeps its sharp fit edges.
    r_out = bore_dia / 2 + 1.5
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and math.hypot(e.center().X, e.center().Y) > r_out
    )
    return polish(body, keep, 1.0)
