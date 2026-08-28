from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.65,
    bore_depth=12.0,
    knob_height=15.0,
    grip_width=36.0,
    grip_waist=30.0,
    finger_scallops=5,
    rim_thickness=3.0,
    hub_wall=3.2,
    spoke_width=3.4,
    draft=False,
):
    """A replacement valve knob: printed bore up, flipped onto the stem in use.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how far the stem's flat sits from the round side opposite it
    bore_clearance: extra room in the bore so the knob slides onto the stem
    bore_depth: how deep the bore runs, so the stem seats all the way in
    knob_height: how tall the knob stands
    grip_width: how far across the knob measures at its widest, over the lobes
    grip_waist: how far across it measures at its narrowest, in the finger scallops
    finger_scallops: how many finger scallops run around the rim
    rim_thickness: how thick the outer grip wall is at a scallop
    hub_wall: how much material wraps the bore
    spoke_width: how wide each spoke from the hub out to the rim is
    """
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    bore_flat = (shaft_across_flat + bore_clearance) - bore_radius
    outer_radius = grip_width / 2.0
    waist_radius = grip_waist / 2.0
    hub_radius = bore_radius + hub_wall
    cap = knob_height - bore_depth
    cavity_radius = waist_radius - rim_thickness

    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter"
            f" {shaft_diameter}, so there is no flat to grip and the knob would"
            " spin on the stem",
            param="shaft_across_flat",
        )
    if waist_radius <= hub_radius + 2.0 * rim_thickness:
        reject(
            f"grip_waist {grip_waist} leaves no room between the hub and the rim:"
            f" raise it above {2.0 * (hub_radius + 2.0 * rim_thickness):.1f}",
            param="grip_waist",
        )
    if grip_width <= grip_waist:
        reject(
            f"grip_width {grip_width} is not over grip_waist {grip_waist}, so the"
            " scallops vanish and wet hands slip",
            param="grip_width",
        )
    if cap < 2.0:
        reject(
            f"bore_depth {bore_depth} leaves a {cap:.1f}mm cap over the bore:"
            f" keep it under {knob_height - 2.0:.1f}",
            param="bore_depth",
        )

    # The outline: a disc with a finger scallop bitten out between each lobe.
    scallop_radius = 2.0 * (outer_radius - waist_radius)
    outline = Circle(outer_radius)
    for i in range(finger_scallops):
        outline -= (
            Rot(0, 0, i * 360.0 / finger_scallops)
            * Pos(waist_radius + scallop_radius, 0)
            * Circle(scallop_radius)
        )
    body = extrude(outline, knob_height)

    # The D-bore, opening up as it prints, blind at the bed so the far end caps it.
    keyway = Circle(bore_radius) - Pos(
        bore_flat + bore_radius, 0
    ) * Rectangle(2.0 * bore_radius, 4.0 * bore_radius)
    body -= Pos(0, 0, cap) * extrude(keyway, bore_depth + 1.0)

    # Hollow the ring between hub and rim, leaving a spoke under every lobe.
    pocket = Circle(cavity_radius) - Circle(hub_radius)
    for i in range(finger_scallops):
        pocket -= (
            Rot(0, 0, (i + 0.5) * 360.0 / finger_scallops)
            * Pos(cavity_radius / 2.0, 0)
            * Rectangle(cavity_radius + 1.0, spoke_width)
        )
    body -= Pos(0, 0, cap) * extrude(pocket, bore_depth + 1.0)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)

    def exposed(e):
        bb = e.bounding_box()
        if bb.max.Z <= bed + 1e-6:  # lying in the bed face
            return False
        if any(e.is_same(c) for c in concave):
            return False
        reach = max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y))
        if reach <= bore_radius + 0.05:  # the bore mouth is mating geometry
            return False
        return True

    return polish(body, body.edges().filter_by(exposed), 1.0)
