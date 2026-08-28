from nurb import *


@part
def valve_knob(
    shaft_diameter: float = 8.0,
    shaft_across_flat: float = 6.5,
    knob_height: float = 15.0,
    grip_radius: float = 14.5,
    draft: bool = False,
):
    """A two-wing replacement knob for a D-shaped valve stem.

    shaft_diameter: the stem's diameter across its round section.
    shaft_across_flat: distance from the stem's flat to its opposite round side.
    knob_height: overall printed height, from the bed to the top.
    grip_radius: radius of the round central palm grip.
    """
    # The allowance is bounded: a 0.3 mm oversized virtual shaft clears,
    # while a 1.0 mm oversize jams and cannot rattle in service.
    fit_clearance = 0.70
    bore_radius = (shaft_diameter + fit_clearance) / 2
    bore_across_flat = shaft_across_flat + fit_clearance
    flat_plane = bore_across_flat - bore_radius
    bore_depth = min(knob_height - 2.5, 12.5)

    if bore_depth <= 10.0:
        reject("knob_height must leave a 10 mm-deep stem bore", "knob_height")
    if bore_across_flat >= 2 * bore_radius:
        reject("shaft_across_flat must be smaller than shaft_diameter", "shaft_across_flat")

    # A round palm disk guarantees a broad continuous grip. The opposing wings
    # make the maximum reach noticeably larger than its narrowest span.
    wing_radius = grip_radius * 0.43
    wing_offset = grip_radius * 0.72
    body = Cylinder(grip_radius, knob_height)
    body += Cylinder(wing_radius, knob_height).translate((wing_offset, 0, 0))
    body += Cylinder(wing_radius, knob_height).translate((-wing_offset, 0, 0))

    # Bore-up orientation: the cutter opens at the top and its flat faces +X.
    # Filling the circular cutter past flat_plane leaves a true D profile.
    cutter_height = bore_depth + 0.05
    cutter_z = knob_height / 2 - bore_depth + cutter_height / 2
    bore = Cylinder(bore_radius, cutter_height).translate((0, 0, cutter_z))
    fill_width = bore_radius + 1.0
    flat_fill = Box(
        fill_width,
        2 * (bore_radius + 1.0),
        bore_depth,
    ).translate(
        (flat_plane + fill_width / 2, 0, knob_height / 2 - bore_depth / 2)
    )
    knob = (body - bore) + flat_fill

    # Keep the bed contact broad and the D-bore dimensionally plain; soften
    # only exterior top and side edges for a comfortable finished grip.
    bed = knob.bounding_box().min.Z
    outer_edges = knob.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > bed
        and edge.bounding_box().min.X < -bore_radius - 0.2
    )
    return knob if draft else polish(knob, outer_edges, 0.8)
