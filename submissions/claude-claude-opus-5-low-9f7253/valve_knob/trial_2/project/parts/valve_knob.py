from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    bore_clearance=0.6,
    knob_height=14.0,
    body_width=29.2,
    lobe_reach=34.0,
    lobe_width=8.0,
    lobe_count=4,
    floor_thickness=2.0,
    draft=False,
):
    """A replacement valve knob that presses onto a D-shaped stem.

    shaft_diameter: the round size of the valve stem, measured across
    shaft_across_flat: the stem measured from its flat to the round side
    bore_clearance: extra size in the bore so the knob slips on without rattling
    knob_height: how tall the knob stands
    body_width: how wide the round body of the knob is, across
    lobe_reach: how far the finger lobes reach out from the centre, across
    lobe_width: how thick each finger lobe is
    lobe_count: how many finger lobes go around the knob
    floor_thickness: the solid plastic left under the bore
    """
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    flat_offset = shaft_across_flat + bore_clearance / 2.0 - shaft_diameter / 2.0
    bore_depth = knob_height - floor_thickness

    if flat_offset >= bore_radius:
        reject(
            "shaft_across_flat is at or past the full shaft_diameter, so there is no "
            "flat left to grip: lower it below %.2f" % (shaft_diameter / 2.0 + bore_radius - bore_clearance / 2.0),
            param="shaft_across_flat",
        )
    if bore_depth < 10.0:
        reject(
            "the bore would be under 10mm deep and the stem stands 12 proud: raise "
            "knob_height above %.1f" % (10.0 + floor_thickness),
            param="knob_height",
        )
    if body_width / 2.0 - bore_radius < 3.0:
        reject(
            "less than 3mm of wall between the bore and the outside: raise body_width "
            "above %.1f" % ((bore_radius + 3.0) * 2.0),
            param="body_width",
        )

    body_radius = body_width / 2.0
    lobe_radius = lobe_width / 2.0
    lobe_centre = lobe_reach / 2.0 - lobe_radius

    profile = Circle(body_radius)
    for i in range(lobe_count):
        angle = 360.0 / lobe_count * i
        profile += Rot(Z=angle) * Pos(lobe_centre, 0) * Circle(lobe_radius)

    body = extrude(profile, knob_height)

    bore = Circle(bore_radius) & Pos(
        (flat_offset - bore_radius * 2.0) / 2.0, 0
    ) * Rectangle(bore_radius * 2.0 + flat_offset, bore_radius * 4.0)
    body -= Pos(0, 0, knob_height - bore_depth) * extrude(bore, bore_depth + 1.0)

    if draft:
        return body

    top = knob_height
    concave = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 0.01
        and e.bounding_box().max.X - e.bounding_box().min.X + 0.0 >= 0.0
        and e not in concave
        and e.distance_to((0, 0, top)) > bore_radius + 1.5
    )
    return polish(body, keep, 1.0)
