from nurb import *


@part
def valve_knob(
    shaft_diameter: float = 8.0,
    shaft_across_flat: float = 6.5,
    knob_height: float = 15.0,
):
    """Replacement valve knob printed bore-up.

    shaft_diameter: measured diameter across the rounded sides of the D-shaft
    shaft_across_flat: measured distance from the shaft flat to its round side
    knob_height: total printed height of the knob
    """
    # The central barrel guarantees a broad, stable print footprint.  Four
    # overlapping lobes give wet hands positive places to push without making
    # the whole knob unnecessarily large.
    hub_radius = 14.5
    lobe_radius = 6.7
    lobe_offset = 10.8
    body = Cylinder(hub_radius, knob_height)
    for x, y in ((lobe_offset, 0), (-lobe_offset, 0), (0, lobe_offset), (0, -lobe_offset)):
        body = body.fuse(Cylinder(lobe_radius, knob_height).translate((x, y, 0)))

    # Polish the outside before opening the bore so the precision D profile is
    # not altered by the cosmetic edge treatment.
    body_bed = body.bounding_box().min.Z
    body_edges = body.edges().filter_by(lambda edge: edge.bounding_box().min.Z > body_bed)
    body = polish(body, body_edges, 1.0)

    # A D bore has controlled diametral clearance for the measured stem.
    # The +X face is the flat: its location follows from a diameter and the
    # measured distance from the flat to the opposite round side.
    bore_clearance = 0.8
    bore_diameter = shaft_diameter + bore_clearance
    bore_radius = bore_diameter / 2
    bore_across_flat = shaft_across_flat + bore_clearance
    flat_x = -bore_radius + bore_across_flat

    bore_depth = 12.5
    bore_center_z = knob_height / 2 - bore_depth / 2 + 0.1
    round_bore = Cylinder(bore_radius, bore_depth + 0.2).translate((0, 0, bore_center_z))
    flat_cut = Box(2 * bore_radius, 4 * bore_radius, bore_depth + 0.4).translate(
        (flat_x + bore_radius, 0, bore_center_z)
    )
    d_bore = round_bore.cut(flat_cut)
    return body.cut(d_bore)
