from nurb import *
import math


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_width=29.0,
    lobe_reach=4.0,
    lobe_count=2,
    knob_height=13.0,
    bore_clearance=0.6,
    draft=False,
):
    """A replacement valve knob for a D-shaft stem, printed bore-up.

    shaft_diameter: the stem's full diameter, round side to round side
    shaft_across_flat: the stem measured from the flat to the round side
    knob_width: how wide the grip is across its narrowest
    lobe_reach: how far each finger lobe sticks out past the body
    lobe_count: how many finger lobes around the rim
    knob_height: how tall the knob is
    bore_clearance: extra room in the bore so the stem slides in
    """
    body_radius = knob_width / 2.0
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    # The D-bore's flat sits this far from the axis, on the +X side.
    flat_offset = (shaft_across_flat + bore_clearance) - bore_radius

    if flat_offset <= 0 or flat_offset >= bore_radius:
        reject(
            "shaft_across_flat must be between half and the whole of "
            "shaft_diameter for a D-bore to exist",
            param="shaft_across_flat",
        )
    if body_radius < bore_radius + 3.0:
        reject(
            "knob_width leaves under 3mm of wall around the bore: widen it",
            param="knob_width",
        )

    # Grip: a round body with lobes reaching past it.
    body = Cylinder(body_radius, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lobe_center_r = body_radius + lobe_reach / 2.0
    lobe_radius = lobe_reach  # overlaps the body by half its reach
    for i in range(lobe_count):
        a = 2 * math.pi * i / lobe_count
        lobe = Cylinder(
            lobe_radius, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        ).translate((lobe_center_r * math.cos(a), lobe_center_r * math.sin(a), 0))
        body = body + lobe

    # D-profile bore straight through, flat facing +X: a circle with the
    # segment beyond the flat kept as material.
    bore_profile = Circle(bore_radius) & Rectangle(
        bore_radius + flat_offset, 2 * bore_radius,
        align=(Align.MAX, Align.CENTER),
    ).translate((flat_offset, 0))
    bore = extrude(bore_profile, knob_height)
    body = body - bore

    if draft:
        return body

    # Polish exposed edges; leave the bed edges and the bore's mating rim alone.
    bed = body.bounding_box().min.Z
    def far_from_axis(e):
        bb = e.bounding_box()
        r = max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y))
        return r > bore_radius + 1.0

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and far_from_axis(e)
    )
    return polish(body, keep, 1.0)
