from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    shaft_length=measured("shaft_length"),
    bore_clearance=0.65,
    knob_width=34.8,
    knob_height=16.0,
    cap_thickness=3.4,
    grip_count=6,
    scoop_depth=2.8,
    scoop_radius=4.0,
    rim_thickness=2.6,
    hub_wall=3.2,
    draft=False,
):
    """A scalloped valve knob with a D bore, modelled and printed bore-up.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how wide the stem measures from its flat over to the round side
    shaft_length: how far the stem stands proud of the valve body
    bore_clearance: how much wider than the stem the bore is cut, so it slides on
    knob_width: across the knob at its widest, ridge to opposite ridge
    knob_height: how tall the knob stands
    cap_thickness: the closed end that covers the stem tip, the top once it is on
    grip_count: how many finger scoops run around the rim
    scoop_depth: how deep each finger scoop bites into the rim
    scoop_radius: how round each finger scoop is
    rim_thickness: the outer wall left standing around the hollow
    hub_wall: how much material wraps around the bore
    """
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    flat_x = shaft_across_flat + bore_clearance - bore_radius
    bore_depth = knob_height - cap_thickness
    outer_radius = knob_width / 2.0
    valley_radius = outer_radius - scoop_depth
    hub_radius = bore_radius + hub_wall
    hollow_radius = valley_radius - rim_thickness
    scoop_centre = valley_radius + scoop_radius

    if flat_x >= bore_radius:
        reject(
            f"shaft_across_flat {shaft_across_flat} leaves no flat on a "
            f"{shaft_diameter}mm stem, so the knob would spin on it: drop it below "
            f"{shaft_diameter - bore_clearance:.2f}",
            param="shaft_across_flat",
        )
    if cap_thickness < 2.5:
        reject(
            f"cap_thickness {cap_thickness} is under the 2.5mm this design carries over "
            "the stem tip: raise it to 2.5 or more",
            param="cap_thickness",
        )
    if bore_depth < shaft_length + 0.3:
        reject(
            f"a {bore_depth:.2f}mm bore bottoms out on a {shaft_length}mm stem before the "
            f"knob seats: raise knob_height past {shaft_length + 0.3 + cap_thickness:.2f}",
            param="knob_height",
        )
    if hollow_radius - hub_radius < 2.5:
        reject(
            f"the hollow is only {hollow_radius - hub_radius:.2f}mm wide between hub and "
            f"rim: widen knob_width past "
            f"{2 * (hub_radius + 2.5 + rim_thickness + scoop_depth):.2f}",
            param="knob_width",
        )
    ridge_gap = 2.0 * scoop_centre * sin(pi / grip_count) - 2.0 * scoop_radius
    if ridge_gap < 3.0:
        reject(
            f"{grip_count} scoops at {scoop_radius}mm leave {ridge_gap:.2f}mm of ridge "
            "between them, which is nothing to grip: fewer scoops or a smaller scoop_radius",
            param="scoop_radius",
        )

    # Outline: a disc with a ring of finger scoops milled into it. The ridges the scoops
    # leave are rounded off here in 2D, so the outside is one tangent surface and the top
    # rim chamfer runs it as a single unbroken band with no corner slivers.
    outline = Circle(outer_radius)
    for i in range(grip_count):
        a = 2.0 * pi * i / grip_count
        outline -= Pos(scoop_centre * cos(a), scoop_centre * sin(a)) * Circle(scoop_radius)
    outline = fillet(outline.vertices(), 1.5)
    body = extrude(outline, knob_height)

    # Hollow: one ring pocket between hub and rim, opening straight up as it prints, so
    # nothing bridges and the knob is a shell rather than a puck of plastic.
    hollow = Circle(hollow_radius) - Circle(hub_radius)
    body -= Pos(0, 0, knob_height) * extrude(hollow, -bore_depth)

    # The D bore, flat facing +X, mouth at the top face where the stem enters. Its floor
    # lands on the same plane as the hollow's: one cap, one thickness.
    reach = 4.0 * bore_radius
    dee = Circle(bore_radius) - Pos(flat_x + reach / 2.0, 0) * Rectangle(reach, reach)
    body -= Pos(0, 0, knob_height) * extrude(dee, -bore_depth)

    if draft:
        return body

    # Polish the top rim and the mouth of the hollow. The bed face keeps its sharp edges,
    # and the bore is mating geometry, so it gets no lead-in.
    def in_top_face(e):
        box = e.bounding_box()
        return abs(box.min.Z - knob_height) < 1e-6 and abs(box.max.Z - knob_height) < 1e-6

    def clear_of_bore(e):
        box = e.bounding_box()
        return max(abs(box.min.X), abs(box.max.X), abs(box.min.Y), abs(box.max.Y)) > bore_radius + 0.2

    rim = body.edges().filter_by(lambda e: in_top_face(e) and clear_of_bore(e))
    return polish(body, rim, 1.0)
