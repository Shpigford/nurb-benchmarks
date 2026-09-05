import math

from nurb import *


@part
def valve_knob(
    knob_width=40.0,
    knob_height=20.0,
    grip_notch_count=6,
    grip_notch_depth=3.5,
    fit_clearance=0.4,
    bore_extra_depth=2.0,
    chamfer_size=1.0,
    draft=False,
):
    """A push-on replacement knob for a hose valve with a D-shaped stem.

    knob_width: how wide the knob is across, edge to edge
    knob_height: how tall the knob stands off the valve body
    grip_notch_count: how many finger notches around the side
    grip_notch_depth: how deep each finger notch cuts in
    fit_clearance: extra room in the hole over the measured stem; raise if tight, lower if it rattles
    bore_extra_depth: spare depth in the hole past the stem so the knob seats on the valve, not the stem tip
    chamfer_size: size of the edge chamfers
    """
    shaft_diameter = measured("shaft_diameter")
    shaft_across_flat = measured("shaft_across_flat")
    stem_length = measured("stem_length")

    knob_radius = knob_width / 2.0
    bore_radius = (shaft_diameter + fit_clearance) / 2.0
    # The flat sits at the measured across-flat distance from the round side,
    # opened up by the same clearance, with the flat facing +X.
    flat_x = (shaft_across_flat + fit_clearance) - bore_radius
    bore_depth = stem_length + bore_extra_depth
    floor = knob_height - bore_depth

    if fit_clearance < 0.1:
        reject(
            "fit_clearance under 0.1 is a bind that varies by machine, not a tighter "
            "fit: keep it at 0.1 or more (0.4 is the snug default)",
            param="fit_clearance",
        )
    if floor < 3.0:
        reject(
            f"knob_height {knob_height} leaves only {floor:.1f}mm of material under the "
            f"{bore_depth:.1f}mm stem hole; raise it above {bore_depth + 3.0:.1f}",
            param="knob_height",
        )
    grip_wall = knob_radius - grip_notch_depth - bore_radius
    if grip_wall < 3.0:
        reject(
            f"only {grip_wall:.1f}mm of wall is left between the finger notches and the "
            f"stem hole; widen knob_width above "
            f"{2 * (bore_radius + grip_notch_depth + 3.0):.1f} or shallow the notches",
            param="knob_width",
        )

    body = Pos(0, 0, knob_height / 2) * Cylinder(knob_radius, knob_height)

    # Finger notches: vertical scallops around the rim, evenly spaced. All-vertical
    # geometry, so they print support-free in any count.
    if grip_notch_count > 0:
        notch_radius = grip_notch_depth + 1.5
        notch_width = 2 * math.sqrt(notch_radius**2 - (notch_radius - grip_notch_depth) ** 2)
        if grip_notch_count * (notch_width + 2.0) > math.pi * knob_width:
            reject(
                f"{grip_notch_count} finger notches will not fit around a "
                f"{knob_width}mm knob without merging; use "
                f"{int(math.pi * knob_width // (notch_width + 2.0))} or fewer",
                param="grip_notch_count",
            )
        for i in range(grip_notch_count):
            angle = i * 360.0 / grip_notch_count
            body -= Rot(0, 0, angle) * (
                Pos(knob_radius + notch_radius - grip_notch_depth, 0, knob_height / 2)
                * Cylinder(notch_radius, knob_height + 2)
            )

    # The D-bore: a blind vertical pocket from the top face, flat facing +X so the
    # knob drives the stem instead of spinning on it. Vertical and open upward, so
    # it needs no support and its floor is solid material to the bed.
    bore = Pos(0, 0, knob_height - bore_depth / 2) * Cylinder(bore_radius, bore_depth)
    bore -= Pos(flat_x + bore_radius, 0, knob_height - bore_depth / 2) * Box(
        2 * bore_radius, 2 * bore_radius + 2, bore_depth + 2
    )
    body -= bore

    if draft:
        return body

    # Polish: chamfer exposed edges, excluding the bed face, concave junctions,
    # and the bore mouth (fit-critical: no lead-in chamfer).
    bed = body.bounding_box().min.Z
    concave = [e.center() for e in concave_edges(body)]

    def radial_reach(e):
        bb = e.bounding_box()
        return max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y))

    keep = (
        body.edges()
        .filter_by(lambda e: e.bounding_box().min.Z > bed)
        .filter_by(lambda e: radial_reach(e) > bore_radius + 1.0)
        .filter_by(lambda e: all((e.center() - c).length > 1e-3 for c in concave))
    )
    return polish(body, keep, chamfer_size)
