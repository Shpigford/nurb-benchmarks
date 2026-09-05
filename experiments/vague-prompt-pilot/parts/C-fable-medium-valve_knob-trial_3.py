import math

from nurb import *


@part
def valve_knob(
    knob_width=38.0,
    knob_floor=4.0,
    grip_notch_count=6,
    grip_notch_depth=2.5,
    fit_clearance=0.3,
    chamfer_size=1.0,
    draft=False,
):
    """Replacement push-on knob for a hose valve with a D-shaped stem.

    knob_width: how wide the knob is across, edge to edge
    knob_floor: how much solid plastic sits above the end of the stem
    grip_notch_count: how many finger notches around the rim
    grip_notch_depth: how deep each finger notch cuts into the rim
    fit_clearance: extra room in the stem hole; raise it if the knob is too tight
    chamfer_size: size of the edge bevels
    """
    shaft_dia = measured("shaft_diameter")
    across_flat = measured("shaft_across_flat")
    stem_length = measured("stem_length")

    bore_dia = shaft_dia + fit_clearance
    bore_r = bore_dia / 2
    # Flat faces +X. Flat-to-round across the bore stays across_flat + fit_clearance.
    flat_x = across_flat + fit_clearance - bore_r
    bore_depth = stem_length + 1.0
    height = bore_depth + knob_floor

    min_width = bore_dia + 2 * (3.0 + grip_notch_depth) + 2.0
    if knob_width < min_width:
        reject(
            f"knob_width {knob_width:g} leaves under 3mm of wall between the "
            f"{bore_dia:g}mm stem hole and the finger notches: raise it above "
            f"{min_width:g}",
            param="knob_width",
        )
    if grip_notch_count < 3:
        reject(
            "grip_notch_count under 3 leaves nothing for fingers to catch: "
            "use 3 or more",
            param="grip_notch_count",
        )

    body = Cylinder(
        knob_width / 2, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Finger notches: vertical scallops cut into the rim, self-supporting as printed.
    notch_r = math.pi * knob_width / grip_notch_count / 3.0
    notch_center = knob_width / 2 + notch_r - grip_notch_depth
    notches = [
        Pos(
            notch_center * math.cos(math.radians(a)),
            notch_center * math.sin(math.radians(a)),
        )
        * Cylinder(notch_r, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for a in [i * 360.0 / grip_notch_count for i in range(grip_notch_count)]
    ]
    for n in notches:
        body -= n

    # D-bore, opening straight up, flat toward +X, blind above a solid floor.
    profile = Circle(bore_r) - Pos(flat_x + bore_r, 0) * Rectangle(
        2 * bore_r, 2 * bore_dia
    )
    body -= Pos(0, 0, height) * extrude(profile, amount=-bore_depth)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    bore_guard = bore_r + 1.0
    concave = {
        (round(e.center().X, 2), round(e.center().Y, 2), round(e.center().Z, 2))
        for e in concave_edges(body)
    }

    def polishable(e):
        bb = e.bounding_box()
        if bb.max.Z <= bed + 1e-6:
            return False  # lies in the bed face
        if all(math.hypot(v.X, v.Y) <= bore_guard for v in e.vertices()):
            return False  # the bore is mating geometry: no lead-in chamfer
        c = e.center()
        if (round(c.X, 2), round(c.Y, 2), round(c.Z, 2)) in concave:
            return False
        return True

    keep = body.edges().filter_by(polishable)
    return polish(body, keep, chamfer_size)
