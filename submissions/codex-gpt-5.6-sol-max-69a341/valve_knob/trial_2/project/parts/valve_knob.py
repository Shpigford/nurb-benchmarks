from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A support-free replacement knob for a D-shaped valve stem.

    shaft_diameter: diameter across the rounded portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than 0mm", param="shaft_diameter")
    if shaft_across_flat <= shaft_diameter / 2.0:
        reject(
            "shaft_across_flat must be more than half shaft_diameter",
            param="shaft_across_flat",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter so the flat can transmit torque",
            param="shaft_across_flat",
        )

    knob_width = 30.0
    knob_height = 15.5
    bore_depth = 12.4
    bore_clearance = 0.7
    polish_size = 1.2

    body = Box(
        knob_width,
        knob_width,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Add equal diametral clearance to both measured D-shaft dimensions.  The
    # clipping plane is on +X, so the finished socket's flat faces +X too.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = -bore_radius + bore_across_flat
    bore_floor_z = knob_height - bore_depth
    cutter_height = bore_depth + 0.2

    round_cutter = Cylinder(
        bore_radius,
        cutter_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, bore_floor_z))
    flat_limit = Box(
        bore_diameter + 2.0,
        bore_diameter + 2.0,
        cutter_height,
        align=(Align.MAX, Align.CENTER, Align.MIN),
    ).translate((bore_flat_x, 0.0, bore_floor_z))
    bore = round_cutter & flat_limit
    body = body - bore

    if draft:
        return body

    bed_z = body.bounding_box().min.Z
    exposed_outer_edges = body.edges().filter_by(
        lambda edge: (
            edge.bounding_box().max.Z > bed_z + 0.01
            and max(
                abs(edge.bounding_box().min.X),
                abs(edge.bounding_box().max.X),
                abs(edge.bounding_box().min.Y),
                abs(edge.bounding_box().max.Y),
            )
            > 10.0
        )
    )
    return polish(body, exposed_outer_edges, polish_size)
