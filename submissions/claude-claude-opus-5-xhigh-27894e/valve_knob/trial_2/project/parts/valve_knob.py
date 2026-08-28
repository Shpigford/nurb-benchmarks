from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    stem_gap=0.3,
    socket_depth=12.6,
    cap_thickness=3.0,
    knob_width=29.0,
    lobe_reach=17.0,
    lobe_width=10.0,
    lobe_count=3,
    valley_blend=3.0,
    chamfer_size=1.0,
    draft=False,
):
    """A replacement valve knob: a D-socket that drives the stem, three lobes to grip.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how wide the stem measures from its flat to the round side
    stem_gap: gap left between the stem and the socket wall, on every side
    socket_depth: how deep the socket goes, measured down from its mouth
    cap_thickness: solid material over the end of the stem, the knob's top in use
    knob_width: how wide the round body is, measured between the lobes
    lobe_reach: how far each grip lobe reaches out from the centre
    lobe_width: how fat each grip lobe is where the hand grabs it
    lobe_count: how many grip lobes go round the knob
    valley_blend: how softly each lobe runs back into the body
    chamfer_size: the chamfer taken off exposed edges
    """
    # The socket is one offset outward from the stem on every surface: the round wall
    # moves out by stem_gap, and so does the flat.
    socket_radius = shaft_diameter / 2 + stem_gap
    socket_flat = shaft_across_flat - shaft_diameter / 2 + stem_gap
    knob_height = cap_thickness + socket_depth

    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}: a D-shaft's flat cuts into the circle, so keep it "
            f"below {shaft_diameter - 0.5}",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter * 0.6:
        reject(
            f"shaft_across_flat {shaft_across_flat} cuts past the middle of a "
            f"{shaft_diameter}mm stem, which is a half-round rather than a D: raise it "
            f"above {shaft_diameter * 0.6:.1f}",
            param="shaft_across_flat",
        )
    if knob_width / 2 - socket_radius < 3.0:
        reject(
            f"knob_width {knob_width} leaves {knob_width / 2 - socket_radius:.1f}mm of "
            f"wall around the socket, which splits under hand torque: raise it above "
            f"{2 * (socket_radius + 3.0):.1f}",
            param="knob_width",
        )
    if lobe_reach <= knob_width / 2 + 1.0:
        reject(
            f"lobe_reach {lobe_reach} does not clear the {knob_width}mm body: the lobes "
            f"are the grip, so raise it above {knob_width / 2 + 1.0:.1f}",
            param="lobe_reach",
        )
    if lobe_reach - lobe_width >= knob_width / 2:
        reject(
            f"a {lobe_width}mm lobe reaching {lobe_reach} floats clear of the "
            f"{knob_width}mm body: widen it past {2 * (lobe_reach - knob_width / 2):.1f}",
            param="lobe_width",
        )

    # Plan view: one round body with lobes standing off it, the valleys between them
    # blended so the hand meets a curve rather than a corner.
    lobe_radius = lobe_width / 2
    lobe_centre = lobe_reach - lobe_radius
    plan = Circle(knob_width / 2)
    for i in range(lobe_count):
        around = radians(360 * i / lobe_count)
        plan += Pos(lobe_centre * cos(around), lobe_centre * sin(around)) * Circle(lobe_radius)
    plan = fillet(plan.vertices(), valley_blend)

    # The D of the socket: the stem's circle with everything past the flat taken off,
    # flat facing +X, printed mouth up so the bore is self-supporting.
    d_stem = Circle(socket_radius) - Pos(socket_flat + socket_radius, 0) * Rectangle(
        2 * socket_radius, 4 * socket_radius
    )

    knob = extrude(plan, knob_height)
    knob -= Pos(0, 0, cap_thickness) * extrude(d_stem, socket_depth + 1.0)

    if draft:
        return knob

    # Polish the outer rim at the mouth end only. The bed face is the knob's top in use
    # and its edges lie in that face; the socket mouth is mating geometry and a lead-in
    # chamfer there prints as a compound sliver.
    bed = knob.bounding_box().min.Z
    mouth_reach = socket_radius + 2.0

    def outer_rim(e):
        box = e.bounding_box()
        if box.min.Z <= bed + 0.01:
            return False
        corners = (box.min.X, box.max.X, box.min.Y, box.max.Y)
        return max(abs(c) for c in corners) > mouth_reach

    return polish(knob, knob.edges().filter_by(outer_rim), chamfer_size)
