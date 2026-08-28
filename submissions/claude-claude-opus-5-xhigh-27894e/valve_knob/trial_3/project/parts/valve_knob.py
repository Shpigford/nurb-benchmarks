from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.6,
    knob_height=15.0,
    floor_thickness=2.5,
    body_radius=14.6,
    lobe_count=3,
    lobe_radius=6.0,
    lobe_reach=17.6,
    blend_radius=3.0,
    draft=False,
):
    """A replacement knob for a D-shaft valve stem, modelled bore-up as it prints.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how far it measures from the flat to the opposite round side
    bore_clearance: total slack the bore adds over the stem, so it slips on but does not rattle
    knob_height: how tall the knob stands
    floor_thickness: how much solid plastic caps the bore at the bed side
    body_radius: how far the round waist of the knob reaches from the centre
    lobe_count: how many finger lobes go around the knob
    lobe_radius: how fat each finger lobe is
    lobe_reach: how far the tip of a lobe reaches from the centre
    blend_radius: how softly a lobe blends back into the waist
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}: a D-shaft measures less across the flat than across the "
            f"round, so there is no flat here to drive against. Lower it below "
            f"{shaft_diameter}.",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter * 0.55:
        reject(
            f"shaft_across_flat {shaft_across_flat} cuts more than half of a "
            f"{shaft_diameter} stem away, which is a half-round, not a D-shaft: raise it "
            f"above {round(shaft_diameter * 0.55, 2)}.",
            param="shaft_across_flat",
        )
    if bore_clearance < 0.4:
        reject(
            f"bore_clearance {bore_clearance} is under the 0.4 a printed bore needs to "
            f"drop onto a stem it has to be square with: raise it to 0.4 or more.",
            param="bore_clearance",
        )
    if bore_clearance > 0.8:
        reject(
            f"bore_clearance {bore_clearance} lets the knob rock on the flat instead of "
            f"turning the valve: lower it to 0.8 or less.",
            param="bore_clearance",
        )
    if floor_thickness < 2.0:
        reject(
            f"floor_thickness {floor_thickness} is under the 2mm minimum wall, and this "
            f"floor is the face a thumb presses while the stem pushes back: raise it to "
            f"2.0 or more.",
            param="floor_thickness",
        )
    if knob_height - floor_thickness < 6.0:
        reject(
            f"knob_height {knob_height} leaves a bore only "
            f"{round(knob_height - floor_thickness, 2)} deep, which cannot hold a stem "
            f"square enough to turn it: raise it above {round(floor_thickness + 6.0, 2)}.",
            param="knob_height",
        )
    if lobe_count < 2 or lobe_count > 8:
        reject(
            f"lobe_count {lobe_count} is outside the 2 to 8 a hand can find: pick a count "
            f"in that range.",
            param="lobe_count",
        )
    if lobe_reach < body_radius * 1.12:
        reject(
            f"lobe_reach {lobe_reach} is less than 12% past the {body_radius} waist, so "
            f"there is nothing standing proud for a wet hand to grab: raise it above "
            f"{round(body_radius * 1.12, 2)}.",
            param="lobe_reach",
        )
    if lobe_reach - 2.0 * lobe_radius > body_radius - 1.0:
        reject(
            f"lobe_radius {lobe_radius} is too small to reach back into the "
            f"{body_radius} waist from a tip at {lobe_reach}, so the lobes would float "
            f"free of the body: raise it above "
            f"{round((lobe_reach - body_radius + 1.0) / 2.0, 2)}.",
            param="lobe_radius",
        )
    if blend_radius >= lobe_radius:
        reject(
            f"blend_radius {blend_radius} is not under lobe_radius {lobe_radius}, so the "
            f"blend would swallow the lobe it is meant to soften: lower it below "
            f"{lobe_radius}.",
            param="blend_radius",
        )

    # The bore is the stem plus one slack figure, spent on both dimensions at once: the
    # round side sets the radius, the flat sits that far back from the opposite round wall.
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    bore_flat = shaft_across_flat + bore_clearance - bore_radius
    bore_depth = knob_height - floor_thickness

    if body_radius - bore_radius < 2.0:
        reject(
            f"body_radius {body_radius} leaves only "
            f"{round(body_radius - bore_radius, 2)} of wall around a {bore_radius * 2} "
            f"bore: raise it above {round(bore_radius + 2.0, 2)}.",
            param="body_radius",
        )

    # A round waist with finger lobes standing off it, blended where they meet so the
    # side is one continuous surface and nothing pinches a hand.
    outline = Circle(body_radius)
    lobe_centre = lobe_reach - lobe_radius
    for i in range(lobe_count):
        outline += (
            Rot(0.0, 0.0, 360.0 * i / lobe_count)
            * Pos(lobe_centre, 0.0)
            * Circle(lobe_radius)
        )
    if blend_radius > 0.0:
        outline = fillet(outline.vertices(), blend_radius)

    body = extrude(outline, knob_height)

    # The D, flat toward +X, cut down from the top face: bore-up is how it prints, and
    # the knob turns over onto the stem in use.
    stem = Circle(bore_radius) - Pos(bore_flat + bore_radius, 0.0) * Rectangle(
        2.0 * bore_radius, 4.0 * bore_radius
    )
    body -= Pos(0.0, 0.0, floor_thickness) * extrude(stem, bore_depth + 1.0)

    if draft:
        return body

    # Keep the bed face and everything standing on it sharp, keep the bore mouth and its
    # floor sharp because the stem has to slide down them, and chamfer the outer top rim.
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.01
        and Vector(e.center().X, e.center().Y, 0.0).length > bore_radius + blend_radius
    )
    return polish(body, keep, 1.0)
