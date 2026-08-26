from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    stem_height=12.0,
    knob_width=28.0,
    lobe_width=9.0,
    lobe_count=3,
    floor_thickness=2.5,
    bore_clearance=0.5,
    draft=False,
):
    """Replacement valve knob with a D-shaped bore, printed bore-up.

    shaft_diameter: the round width of the valve stem
    shaft_across_flat: stem width from the flat to the round side
    stem_height: how far the stem stands proud of the valve body
    knob_width: width of the round core of the knob
    lobe_width: width of each finger lobe on the rim
    lobe_count: how many finger lobes around the rim
    floor_thickness: material above the end of the stem
    bore_clearance: total extra on the bore over the stem so it slides on
    """
    bore_depth = stem_height + 0.5
    height = bore_depth + floor_thickness
    if lobe_count < 2:
        reject("lobe_count must be at least 2 to give the hand a grip", param="lobe_count")

    # Core plus lobes around the rim, so wet hands have something to grab.
    core_r = knob_width / 2
    outline = Circle(core_r)
    for i in range(lobe_count):
        a = 360.0 * i / lobe_count + 90.0
        pos = Vector(core_r, 0, 0).rotate(Axis.Z, a)
        outline = outline + Pos(pos.X, pos.Y, 0) * Circle(lobe_width / 2)
    body = extrude(outline, height)

    # D-shaped bore, flat facing +X, opening at the top face.
    r = (shaft_diameter + bore_clearance) / 2
    flat_x = (shaft_across_flat + bore_clearance) - r
    if flat_x <= -r or flat_x >= r:
        reject("shaft_across_flat must be between zero and shaft_diameter", param="shaft_across_flat")
    d_profile = Circle(r) - Pos(flat_x + r, 0, 0) * Rectangle(2 * r, 4 * r)
    bore = extrude(d_profile, bore_depth)
    bore = bore.moved(Location((0, 0, height - bore_depth)))
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    # Only the outside gets chamfered: the bore's edges are fit geometry.
    def outside(e):
        bb = e.bounding_box()
        return bb.min.Z > bed and max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y)) > r + 0.5

    keep = body.edges().filter_by(outside)
    return polish(body, keep, 1.0)
