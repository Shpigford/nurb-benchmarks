from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    knob_width=40.0,
    knob_height=18.0,
    grip_notch_count=6,
    grip_notch_size=12.0,
    grip_notch_depth=3.0,
    stem_hole_depth=13.0,
    stem_fit_extra=0.2,
    draft=False,
):
    """Replacement knob for a hose valve with a D-shaft stem, printed bore-up.

    knob_width: how wide the knob is across, edge to edge
    knob_height: how tall the knob is from the valve to its face
    grip_notch_count: how many finger notches around the edge
    grip_notch_size: how wide each finger notch is
    grip_notch_depth: how deep each finger notch bites into the edge
    stem_hole_depth: how deep the stem hole goes into the knob
    stem_fit_extra: extra room in the stem hole; more slides on easier
    """
    shaft_diameter = measured("shaft_diameter")
    shaft_across_flat = measured("shaft_across_flat")

    bore_radius = (shaft_diameter + stem_fit_extra) / 2
    # The stem's flat faces +X. Across-flat opening = flat plane to the round
    # side, so the flat plane sits at (opening - bore_radius) from the axis.
    flat_x = (shaft_across_flat + stem_fit_extra) - bore_radius

    floor = knob_height - stem_hole_depth
    if floor < 3.0:
        reject(
            f"stem_hole_depth {stem_hole_depth} leaves only {floor:.1f}mm of face "
            f"above the stem; keep it at least 3mm below knob_height "
            f"({knob_height - 3.0:.1f} or less)",
            param="stem_hole_depth",
        )
    grip_wall = knob_width / 2 - grip_notch_depth - bore_radius
    if grip_wall < shaft_diameter:
        reject(
            f"only {grip_wall:.1f}mm of material between the stem hole and the "
            f"finger notches; the {shaft_diameter}mm stem wants at least that much "
            f"wall, so widen knob_width or shallow the notches",
            param="knob_width",
        )

    body = Cylinder(
        knob_width / 2, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Finger notches: vertical scalloped cuts, self-supporting, grippy when wet.
    notch_orbit = knob_width / 2 + grip_notch_size / 2 - grip_notch_depth
    for i in range(grip_notch_count):
        a = radians(360.0 * i / grip_notch_count)
        body -= Pos(notch_orbit * cos(a), notch_orbit * sin(a), -1) * Cylinder(
            grip_notch_size / 2,
            knob_height + 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # D-shaped blind bore, opening straight up, flat facing +X.
    bore = Pos(0, 0, floor) * Cylinder(
        bore_radius, stem_hole_depth + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    bore -= Pos(flat_x, -bore_radius - 1, floor - 1) * Box(
        bore_radius, 2 * bore_radius + 2, stem_hole_depth + 3, align=Align.MIN
    )
    body -= bore

    if draft:
        return body

    # Chamfer exposed edges; leave the bed edges, the concave notch roots, and
    # the fit-critical bore mouth sharp.
    bed = body.bounding_box().min.Z
    near_bore = bore_radius + 2.0

    def keepable(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed:
            return False
        corner = max(abs(bb.min.X), abs(bb.max.X)) ** 2 + max(
            abs(bb.min.Y), abs(bb.max.Y)
        ) ** 2
        return corner > near_bore**2

    keep = body.edges().filter_by(keepable) - concave_edges(body)
    return polish(body, keep, 1.0)
