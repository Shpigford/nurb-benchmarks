from nurb import *

from math import cos, radians, sin


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    shaft_length=measured("shaft_length"),
    bore_clearance=0.65,
    knob_width=30.0,
    knob_height=15.5,
    lobe_count=3,
    lobe_reach=19.0,
    lobe_width=12.0,
    valley_radius=3.0,
    rim_thickness=3.0,
    top_thickness=3.0,
    hub_thickness=4.0,
    spoke_width=3.0,
    chamfer_size=1.0,
    draft=False,
):
    """A replacement handle for a D-shaft valve stem, modelled bore-up as it prints.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how far the stem measures from its flat to the round side opposite
    shaft_length: how far the stem stands proud of the valve body
    bore_clearance: how much wider than the stem the bore is cut, so the knob slides on
    knob_width: how far the knob measures across at its narrowest, between the lobes
    knob_height: how tall the knob stands
    lobe_count: how many grip lobes go around the knob
    lobe_reach: how far each grip lobe reaches out from the centre
    lobe_width: how fat each grip lobe is across the bump
    valley_radius: how softly the dip between two lobes is rounded
    rim_thickness: how thick the outer grip wall is
    top_thickness: how thick the closed top is (the face that prints against the bed)
    hub_thickness: how much material wraps the bore
    spoke_width: how wide each rib from the hub out to the rim is
    chamfer_size: how big the edge chamfers are
    """
    body_radius = knob_width / 2.0
    lobe_radius = lobe_width / 2.0
    lobe_centre = lobe_reach - lobe_radius
    pocket_radius = body_radius - rim_thickness

    # The bore is the stem's D-profile grown by half the clearance all the way round,
    # so the round side and the flat both keep the same gap.
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    flat_offset = shaft_across_flat - shaft_diameter / 2.0 + bore_clearance / 2.0
    hub_radius = bore_radius + hub_thickness
    bore_depth = knob_height - top_thickness

    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}: a D-shaft measures less across the flat than across the "
            "round, and with no flat the knob cannot turn the valve",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter / 2.0:
        reject(
            f"shaft_across_flat {shaft_across_flat} is at or past the stem centreline "
            f"(shaft_diameter / 2 is {shaft_diameter / 2.0}): raise it above that, or "
            "the stem is not a D-shaft",
            param="shaft_across_flat",
        )
    if bore_depth < shaft_length:
        reject(
            f"the bore is only {bore_depth}mm deep and the stem stands {shaft_length}mm "
            f"proud: raise knob_height above {shaft_length + top_thickness} so the bore "
            "swallows the whole stem",
            param="knob_height",
        )
    if body_radius - bore_radius < 3.0:
        reject(
            f"a {shaft_diameter}mm stem leaves only "
            f"{body_radius - bore_radius:.2f}mm of knob around its bore: raise knob_width "
            f"above {2.0 * (bore_radius + 3.0):.1f}",
            param="knob_width",
        )
    if lobe_reach <= body_radius + 1.0:
        reject(
            f"lobe_reach {lobe_reach} barely clears the {body_radius}mm body: raise it "
            f"above {body_radius + 1.0} or there is nothing for a wet hand to grip",
            param="lobe_reach",
        )
    if lobe_centre >= body_radius + lobe_radius:
        reject(
            f"a lobe {lobe_width}mm across cannot reach {lobe_reach}mm and still touch "
            "the body: widen lobe_width or pull lobe_reach in",
            param="lobe_width",
        )

    # Outline: one circle with a bump per lobe, and the dips between them rounded so the
    # whole rim is one smooth curve for a hand and one smooth band for the chamfer.
    outline = Circle(body_radius)
    for i in range(lobe_count):
        angle = radians(360.0 * i / lobe_count)
        outline += Pos(lobe_centre * cos(angle), lobe_centre * sin(angle)) * Circle(
            lobe_radius
        )
    outline = fillet(outline.vertices(), valley_radius)

    knob = extrude(outline, knob_height)

    # Everything above the closed top is a skirt: rim, hub and ribs, all vertical, so the
    # pocket between them prints open to the sky and needs nothing to hold it up. A slot
    # narrower than 2.5mm is not worth printing, so a small knob or a fat stem stays solid.
    above = Pos(0, 0, top_thickness)
    if pocket_radius - hub_radius >= 2.5:
        knob -= above * extrude(Circle(pocket_radius), bore_depth)
        knob += above * extrude(Circle(hub_radius), bore_depth)

        rib_reach = pocket_radius + rim_thickness / 2.0
        for i in range(lobe_count):
            rib = Pos(rib_reach / 2.0, 0) * Rectangle(rib_reach, spoke_width)
            knob += above * extrude(Rot(0, 0, 360.0 * i / lobe_count) * rib, bore_depth)

    span = 4.0 * bore_radius
    stem = Circle(bore_radius) - Pos(flat_offset + span / 2.0, 0) * Rectangle(span, span)
    knob -= above * extrude(stem, bore_depth)

    if draft:
        return knob

    bed = knob.bounding_box().min.Z
    mating = bore_radius + 0.05

    def signature(edge):
        centre = edge.center()
        return (round(centre.X, 3), round(centre.Y, 3), round(centre.Z, 3))

    inside_corners = {signature(edge) for edge in concave_edges(knob)}

    def exposed(edge):
        box = edge.bounding_box()
        if box.min.Z <= bed + 1e-6:
            return False  # lies in the bed face, which is the knob's top in use
        if signature(edge) in inside_corners:
            return False  # a chamfer on an inside corner is a feather edge
        reach = max(abs(box.min.X), abs(box.max.X), abs(box.min.Y), abs(box.max.Y))
        return reach > mating  # no lead-in at the bore mouth: it has to land on the stem

    return polish(knob, knob.edges().filter_by(exposed), chamfer_size)
