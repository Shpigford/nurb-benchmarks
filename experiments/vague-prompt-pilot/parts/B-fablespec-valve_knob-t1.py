from nurb import *

from math import cos, radians, sin


@part
def valve_knob(
    fit_clearance=0.2,
    knob_diameter=38.0,
    knob_height=17.0,
    bore_depth=13.0,
    grip_scallop_diameter=12.0,
    draft=False,
):
    """Push-on D-bore knob for a hose-valve stem.

    fit_clearance: extra bore room for a snug push-on
    knob_diameter: overall knob width
    knob_height: overall knob height
    bore_depth: how deep the stem pocket is
    grip_scallop_diameter: size of each finger scallop
    """
    shaft_diameter = measured("shaft_diameter")
    shaft_across_flat = measured("shaft_across_flat")

    floor = knob_height - bore_depth
    if floor < 2.0:
        reject(
            f"bore_depth {bore_depth} leaves only {floor}mm of floor; lower bore_depth so the floor is at least 2mm",
            param="bore_depth",
        )
    if fit_clearance < 0.0:
        reject(
            f"fit_clearance {fit_clearance} is negative; raise it to 0 or more",
            param="fit_clearance",
        )

    bore_dia = shaft_diameter + fit_clearance
    across_flat = shaft_across_flat + fit_clearance
    flat_x = across_flat - bore_dia / 2

    body = Cylinder(
        knob_diameter / 2,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    scallop_axis_r = knob_diameter / 2 + 4.0
    for i in range(6):
        ang = radians(i * 60)
        x = scallop_axis_r * cos(ang)
        y = scallop_axis_r * sin(ang)
        body -= Cylinder(
            grip_scallop_diameter / 2,
            knob_height + 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).move(Location((x, y, -1)))

    bore_cyl = Cylinder(
        bore_dia / 2,
        bore_depth + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).move(Location((0, 0, knob_height - bore_depth)))
    flat_cut = Box(
        bore_dia,
        bore_dia + 2,
        bore_depth + 4,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).move(Location((flat_x, 0, knob_height - bore_depth - 1)))
    body -= bore_cyl - flat_cut

    if draft:
        return body

    def _in_bore(e):
        c = e.bounding_box().center()
        return (c.X * c.X + c.Y * c.Y) ** 0.5 < bore_dia / 2 + 2.0

    mouth = body.edges().filter_by(
        lambda e: abs(e.bounding_box().center().Z - knob_height) < 0.05 and _in_bore(e)
    )
    if mouth:
        body = chamfer(mouth, 1.0)

    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and not _in_bore(e)
    )
    return polish(body, keep, 1.0)
