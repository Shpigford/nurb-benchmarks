from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.6,
    bore_depth=measured("shaft_length") + 0.5,
    knob_height=16.0,
    knob_width=30.0,
    grip_ridge_height=3.0,
    grip_count=6,
    skirt_wall=3.5,
    hub_wall=3.2,
    chamfer_size=1.0,
    draft=False,
):
    """A replacement knob for a valve with a D-shaped stem.

    Modelled bore-up, the way it prints; in use it turns over onto the stem.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how far the stem measures from its flat across to the round side
    bore_clearance: how much wider than the stem the bore is cut, so it slides on
    bore_depth: how far up into the knob the stem reaches
    knob_height: how tall the knob is
    knob_width: how far across the knob measures at the finger hollows
    grip_ridge_height: how far the grip ridges stand out past the hollows
    grip_count: how many grip ridges run around the knob
    skirt_wall: how thick the outer wall is at the finger hollows
    hub_wall: how much material stands around the bore
    chamfer_size: how big the chamfer on the finished edges is
    """
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    bore_flat = (shaft_across_flat + bore_clearance) - bore_radius
    hub_radius = bore_radius + hub_wall
    hollow_radius = knob_width / 2.0
    ridge_radius = hollow_radius + grip_ridge_height
    pocket_radius = hollow_radius - skirt_wall
    floor = knob_height - bore_depth

    if floor < 2.0:
        reject(
            f"bore_depth {bore_depth} leaves {floor:.1f}mm over the bore: "
            f"raise knob_height above {bore_depth + 2.0:.1f}",
            param="bore_depth",
        )
    if bore_flat <= 0.5:
        reject(
            f"shaft_across_flat {shaft_across_flat} puts the bore's flat "
            f"{bore_flat:.2f}mm off the axis: the flat has cut past the middle of the stem",
            param="shaft_across_flat",
        )
    if bore_flat >= bore_radius - 0.5:
        reject(
            f"shaft_across_flat {shaft_across_flat} is within half a millimetre of "
            f"the full {shaft_diameter} diameter: the bore has no flat left to drive on",
            param="shaft_across_flat",
        )
    if pocket_radius - hub_radius < 2.0:
        reject(
            f"knob_width {knob_width} leaves {pocket_radius - hub_radius:.1f}mm between hub "
            f"and skirt: widen it past {2 * (hub_radius + skirt_wall + 2.0):.1f}",
            param="knob_width",
        )

    # One smooth periodic wave, so the grip has no vertical corner to chip or to
    # print as a seam: the ridges and the finger hollows are the same curve.
    mid = (ridge_radius + hollow_radius) / 2.0
    swing = (ridge_radius - hollow_radius) / 2.0
    steps = grip_count * 24
    outline = [
        (
            (mid + swing * cos(grip_count * i * 2 * pi / steps)) * cos(i * 2 * pi / steps),
            (mid + swing * cos(grip_count * i * 2 * pi / steps)) * sin(i * 2 * pi / steps),
        )
        for i in range(steps)
    ]
    body = extrude(make_face(Spline(*outline, periodic=True)), knob_height)

    # The skirt is hollow: a ring of air between the hub and the wall, opening
    # upward as it prints and downward toward the valve body in use.
    tall = knob_height + 2.0
    body -= Pos(0, 0, floor) * extrude(Circle(pocket_radius) - Circle(hub_radius), tall)

    # The bore is the stem's own D, grown by bore_clearance on the diameter and on
    # the across-flat alike, which is one uniform offset around the whole profile.
    span = 4 * bore_radius
    stem = Circle(bore_radius) - Pos(bore_flat + span / 2, 0) * Rectangle(span, span)
    body -= Pos(0, 0, floor) * extrude(stem, tall)

    if draft:
        return body

    # Polish the rims that stand at the top of the print and nothing else: the bed
    # face keeps its square first layer, and the bore's mouth is mating geometry.
    def reach(edge):
        box = edge.bounding_box()
        return max(abs(box.min.X), abs(box.max.X), abs(box.min.Y), abs(box.max.Y))

    def in_top_face(edge):
        box = edge.bounding_box()
        return box.min.Z > knob_height - 1e-6 and box.max.Z < knob_height + 1e-6

    keep = body.edges().filter_by(
        lambda e: in_top_face(e) and reach(e) > bore_radius + 0.5
    )
    return polish(body, keep, chamfer_size)
