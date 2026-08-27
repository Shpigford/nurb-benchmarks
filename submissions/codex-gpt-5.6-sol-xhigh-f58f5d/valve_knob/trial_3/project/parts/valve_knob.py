from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A compact replacement valve knob with a clearance D-shaft socket.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    grip_width = 30.0
    knob_height = 15.0
    fit_allowance = 0.6
    stem_proud = 12.0
    socket_end_clearance = 0.4

    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if not 0.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be greater than zero and less than shaft_diameter",
            param="shaft_across_flat",
        )

    bore_diameter = shaft_diameter + fit_allowance
    bore_across_flat = shaft_across_flat + fit_allowance
    bore_radius = bore_diameter / 2.0
    bore_depth = stem_proud + socket_end_clearance
    socket_floor = knob_height - bore_depth

    if grip_width / 2.0 - bore_radius < 3.0:
        reject(
            "shaft_diameter is too large to leave a 3mm wall in this grip",
            param="shaft_diameter",
        )
    if socket_floor < 2.0:
        reject("the socket would leave less than a 2mm floor")

    body = Box(
        grip_width,
        grip_width,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    cutter_height = bore_depth + 0.5
    bore_round = Pos(0, 0, socket_floor) * Cylinder(
        bore_radius,
        cutter_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    bore_clip = Pos(bore_across_flat / 2.0 - bore_radius, 0, socket_floor) * Box(
        bore_across_flat,
        bore_diameter + 1.0,
        cutter_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    bore = bore_round & bore_clip
    knob = body - bore

    if draft:
        return knob

    bed = knob.bounding_box().min.Z
    outer_edge_limit = grip_width / 4.0
    exposed_outer_edges = knob.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > bed + 0.01
        and abs(edge.bounding_box().max.Z - edge.bounding_box().min.Z) < 0.01
        and max(
            abs(edge.bounding_box().min.X),
            abs(edge.bounding_box().max.X),
            abs(edge.bounding_box().min.Y),
            abs(edge.bounding_box().max.Y),
        )
        > outer_edge_limit
    )
    return polish(knob, exposed_outer_edges, 1.0)
