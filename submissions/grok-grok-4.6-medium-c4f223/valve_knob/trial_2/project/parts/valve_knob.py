from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: round diameter of the stem
    shaft_across_flat: distance from the stem's flat to the opposite round
    """
    height = 14.0
    across_flats = 32.0
    clearance = 0.5

    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be under shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )

    bore_diameter = shaft_diameter + clearance
    bore_across_flat = shaft_across_flat + clearance
    bore_r = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_r

    with BuildSketch() as outline:
        RegularPolygon(across_flats / 2.0, 6, major_radius=False)
    body = extrude(outline.sketch, amount=height)

    cutter = Cylinder(
        bore_r,
        height + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0, 0, -1.0))
    clip = Box(
        bore_r * 2.0 + 4.0,
        bore_r * 2.0 + 4.0,
        height + 4.0,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    ).translate((bore_flat_x, 0, height / 2.0))
    body = body - (cutter - clip)

    if draft:
        return body

    top_z = body.bounding_box().max.Z
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top_z) < 1e-4
        and abs(e.bounding_box().max.Z - top_z) < 1e-4
        and (e @ 0.5).X ** 2 + (e @ 0.5).Y ** 2 > (bore_r + 1.0) ** 2
        and e.bounding_box().min.Z > bed
    )
    keep = keep - concave_edges(body)
    return polish(body, keep, 1.0)
