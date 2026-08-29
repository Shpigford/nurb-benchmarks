from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    knob_width=48.0,
    knob_height=20.0,
    grip_scallop=8.0,
    shaft_slack=0.25,
    stem_reach=12.0,
    draft=False,
):
    """Hose-valve replacement knob that presses onto a D-shaft stem.

    knob_width: overall diameter of the grip
    knob_height: printed height, bore opening at the top
    grip_scallop: radius of the finger hollows around the rim
    shaft_slack: extra modelled space around the measured stem, split across the D
    stem_reach: how deep the D-bore is, matching how far the stem sticks out
    """
    shaft_d = measured("shaft_diameter")
    across_flat = measured("shaft_across_flat")
    shaft_r = shaft_d / 2.0

    if shaft_slack < 0.15:
        reject(
            "shaft_slack under 0.15mm will print tighter than a push fit; raise it",
            param="shaft_slack",
        )
    if shaft_slack > 0.45:
        reject(
            "shaft_slack over 0.45mm will rattle on the stem; lower it",
            param="shaft_slack",
        )
    cap = knob_height - stem_reach
    if cap < 3.0:
        reject(
            f"knob_height {knob_height} leaves a {cap:.1f}mm cap over a {stem_reach}mm stem; raise it above {stem_reach + 3.0}",
            param="knob_height",
        )
    if grip_scallop * 2 >= knob_width - (shaft_d + 8.0):
        reject(
            "grip_scallop eats the hub around the stem; shrink the scallop or widen the knob",
            param="grip_scallop",
        )

    body = Cylinder(knob_width / 2.0, knob_height).locate(
        Location((0.0, 0.0, knob_height / 2.0))
    )
    n_scallops = 6
    for i in range(n_scallops):
        ang = i * (2.0 * pi / n_scallops)
        cx = (knob_width / 2.0) * cos(ang)
        cy = (knob_width / 2.0) * sin(ang)
        body -= Cylinder(grip_scallop, knob_height + 2.0).locate(
            Location((cx, cy, knob_height / 2.0))
        )

    bore_r = shaft_r + shaft_slack / 2.0
    # Flat faces +X. True flat is at +(across_flat - radius); push it out by half slack.
    true_flat_x = across_flat - shaft_r
    flat_x = true_flat_x + shaft_slack / 2.0
    d_circle = Circle(bore_r)
    flat_cut = Rectangle(bore_r * 2.0, bore_r * 4.0).locate(
        Location((flat_x + bore_r, 0.0))
    )
    d_profile = d_circle - flat_cut
    bore = extrude(d_profile, stem_reach + 1.0).locate(
        Location((0.0, 0.0, knob_height - stem_reach))
    )
    body -= bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = (body.edges() - concave_edges(body)).filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05 and e.length > 4.0
    )
    return polish(body, keep, 1.0)
