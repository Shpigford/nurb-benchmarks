import math

from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    bore_clearance=0.5,
    grip_width=29.0,
    knob_height=12.5,
    floor_thickness=2.0,
    draft=False,
):
    """A hex knob replacing a broken valve handle, bored for a D-shaft.

    shaft_diameter: how wide the valve stem is across its round side
    shaft_across_flat: how far the stem's flat sits from its round side
    bore_clearance: how much wider the bore is than the stem, total
    grip_width: how wide the knob is across its flat sides
    knob_height: how tall the knob is
    floor_thickness: how much solid material closes the top of the bore
    """
    bore_dia = shaft_diameter + bore_clearance
    flat_x = (shaft_across_flat + bore_clearance) - bore_dia / 2
    bore_depth = knob_height - floor_thickness

    if flat_x <= 0:
        reject(
            "shaft_across_flat is at or under half the shaft_diameter, so the "
            "D-flat would cross the bore's centerline: raise shaft_across_flat "
            f"above {shaft_diameter / 2 - bore_clearance / 2:.1f}",
            param="shaft_across_flat",
        )
    if grip_width < bore_dia + 6.0:
        reject(
            f"grip_width {grip_width} leaves under 3mm of wall around the "
            f"{bore_dia:.1f}mm bore: raise it above {bore_dia + 6.0:.1f}",
            param="grip_width",
        )

    body = extrude(RegularPolygon(grip_width / math.sqrt(3), 6), knob_height)

    # D-shaped bore, opening straight up, the stem's flat facing +X.
    d_profile = Circle(bore_dia / 2) - Pos(flat_x + bore_dia, 0) * Rectangle(
        2 * bore_dia, 2 * bore_dia
    )
    cutter = Pos(0, 0, knob_height) * extrude(d_profile, -bore_depth)
    knob = body - cutter

    if draft:
        return knob

    bed = knob.bounding_box().min.Z

    def exposed(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed:
            return False
        # leave the bore's mating mouth and inner edges alone
        reach = max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y))
        return reach > bore_dia

    keep = knob.edges().filter_by(exposed)
    return polish(knob, keep, 1.0)
