import math

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.65,
    bore_depth=11.5,
    cap_thickness=3.0,
    grip_width=30.0,
    lobe_count=3,
    lobe_reach=18.0,
    lobe_width=12.0,
    wall_thickness=3.0,
    chamfer_size=1.0,
    draft=False,
):
    """A lobed replacement knob that drives a D-shaped valve stem.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how thick the stem measures from its flat to the round side
    bore_clearance: how much wider than the stem the bore is cut, so it slides on without rattling
    bore_depth: how far the bore reaches down into the knob
    cap_thickness: how thick the closed end of the knob is, over the top of the stem
    grip_width: how wide the knob measures across its waist, between the lobes
    lobe_count: how many grip lobes stand around the knob
    lobe_reach: how far a lobe stands out from the centreline
    lobe_width: how wide each lobe is where it bulges out of the waist
    wall_thickness: how thick the outer wall, the ribs and the collar around the bore are
    chamfer_size: how big the chamfers on the handled edges are
    """
    # The knob prints bore-up: the closed cap is the first layer, every wall rises from
    # it, and nothing overhangs. In use it flips over onto the stem, so the printed
    # bottom is the face the hand lands on.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2
    # Where the bore's flat sits, measured from the centreline toward +X. The stem's
    # own flat sits at shaft_across_flat - shaft_diameter / 2, so the clearance opens
    # by half of itself here and the fit is the same slack all the way round.
    flat_offset = bore_across_flat - bore_radius

    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat:g} is not under shaft_diameter "
            f"{shaft_diameter:g}, so the stem has no flat and the knob would spin on it",
            param="shaft_across_flat",
        )
    if flat_offset <= 0.5:
        reject(
            f"shaft_across_flat {shaft_across_flat:g} cuts to the middle of a "
            f"{shaft_diameter:g}mm stem: raise it above "
            f"{shaft_diameter / 2 + 0.5 - bore_clearance / 2:.1f}",
            param="shaft_across_flat",
        )

    waist_radius = grip_width / 2
    lobe_radius = lobe_width / 2
    lobe_centre = lobe_reach - lobe_radius
    collar_radius = bore_radius + wall_thickness
    inner_waist = waist_radius - wall_thickness

    if lobe_reach <= waist_radius + 1.0:
        reject(
            f"lobe_reach {lobe_reach:g} does not clear the {grip_width:g}mm waist: "
            f"raise it above {waist_radius + 1.0:g} or the knob turns round and slips",
            param="lobe_reach",
        )
    if lobe_reach - lobe_width > inner_waist - wall_thickness:
        reject(
            f"lobe_width {lobe_width:g} is too narrow to meet the waist it stands on: "
            f"raise it above {lobe_reach - inner_waist + wall_thickness:.1f}",
            param="lobe_width",
        )
    if inner_waist - collar_radius < 1.0:
        reject(
            f"grip_width {grip_width:g} leaves no room between the bore collar and the "
            f"wall: raise it above {2 * (collar_radius + wall_thickness + 1.0):.1f}",
            param="grip_width",
        )

    height = cap_thickness + bore_depth

    def clover(waist, lobe):
        """The knob's outline: a waist circle with `lobe_count` lobes standing out of it."""
        outline = Circle(waist)
        for i in range(lobe_count):
            angle = 2 * math.pi * i / lobe_count
            outline += Pos(lobe_centre * math.cos(angle), lobe_centre * math.sin(angle)) * Circle(lobe)
        return outline

    body = extrude(clover(waist_radius, lobe_radius), amount=height)

    # Hollow the underside, which is what the knob would otherwise be: a solid puck of
    # plastic around an 8mm stem. The pocket stops at the waist, so the lobes stay solid
    # lugs where the hand pushes, and each bar of ribs ties the collar to the wall under
    # one lobe and under the valley opposite it.
    ribs = Sketch()
    for i in range(lobe_count):
        ribs += Rot(0, 0, 180.0 * i / lobe_count) * Rectangle(2 * inner_waist, wall_thickness)
    pockets = Circle(inner_waist) - Circle(collar_radius) - ribs
    body -= Pos(0, 0, cap_thickness) * extrude(pockets, amount=bore_depth + 1.0)

    # The D bore, cut from the top face down. The flat faces +X, as the stem does.
    profile = Circle(bore_radius) & Pos(flat_offset - bore_radius, 0) * Rectangle(
        2 * bore_radius, 3 * bore_radius
    )
    body -= Pos(0, 0, height - bore_depth) * extrude(profile, amount=bore_depth + 1.0)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)

    def on_the_bore(edge):
        """The bore's own mouth, which is mating geometry and gets no lead-in."""
        return all(math.hypot(v.X, v.Y) <= bore_radius + 0.01 for v in edge.vertices())

    keep = [
        e
        for e in body.edges()
        if e.bounding_box().min.Z > bed + 1e-6 and e not in concave and not on_the_bore(e)
    ]
    return polish(body, keep, chamfer_size)
