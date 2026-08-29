from math import cos, pi, sin

from nurb import *


def _d_profile(bore_r, flat_x):
    d_circle = Circle(bore_r)
    cut_w = bore_r * 4.0
    cut = Rectangle(cut_w, cut_w).move(Location((flat_x + cut_w / 2.0, 0)))
    return d_circle - cut


@part
def valve_knob(
    knob_diameter=50.0,
    knob_height=24.0,
    grip_scallops=8,
    scallop_width=10.0,
    fit_slack=0.20,
    draft=False,
):
    """Replacement knob for a hose valve D-stem.

    knob_diameter: overall grip size, wide enough for wet hands
    knob_height: how tall the knob stands off the valve body
    grip_scallops: number of finger scoops around the rim
    scallop_width: how wide each finger scoop is
    fit_slack: extra space in the D-bore so it pushes on without a hammer
    """
    shaft_d = measured("shaft_diameter")
    across_flat = measured("shaft_across_flat")
    stem_out = measured("stem_stickout")

    if knob_diameter < 28.0:
        reject("knob_diameter is too small to leave wall around the stem", param="knob_diameter")
    if knob_height < stem_out + 4.0:
        reject(
            f"knob_height must leave at least 4mm of roof over a {stem_out}mm stem",
            param="knob_height",
        )
    if fit_slack < 0.05:
        reject("fit_slack under 0.05mm will need a hammer; raise it", param="fit_slack")
    if fit_slack > 0.6:
        reject("fit_slack over 0.6mm will rattle on the stem; lower it", param="fit_slack")
    if scallop_width < 4.0:
        reject("scallop_width is too narrow to print as a grip scoop", param="scallop_width")

    bore_r = (shaft_d + fit_slack) / 2.0
    # Flat faces +X. Round extreme at x = -bore_r; across-flat is round-to-flat.
    flat_x = (across_flat + fit_slack) - bore_r
    bore_depth = stem_out + 0.4
    if knob_height - bore_depth < 3.0:
        reject("roof over the stem would be under 3mm; raise knob_height", param="knob_height")

    body = Cylinder(knob_diameter / 2.0, knob_height)
    body = body.move(Location((0, 0, knob_height / 2.0)))

    n = int(grip_scallops)
    if n >= 3:
        ring = knob_diameter / 2.0
        for i in range(n):
            ang = i * (360.0 / n)
            x = ring * cos(ang * pi / 180.0)
            y = ring * sin(ang * pi / 180.0)
            scoop = Cylinder(scallop_width / 2.0, knob_height + 2.0)
            scoop = scoop.move(Location((x, y, knob_height / 2.0)))
            body -= scoop

    profile = _d_profile(bore_r, flat_x)
    mouth = Circle(bore_r + 0.8)
    body -= extrude(Plane.XY.offset(knob_height - 1.0) * mouth, amount=1.2)
    body -= extrude(Plane.XY.offset(knob_height - bore_depth) * profile, amount=bore_depth + 0.2)

    if draft:
        return body
    bed = body.bounding_box().min.Z
    inner = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05 and e not in inner
    )
    return polish(body, keep, 1.0)
