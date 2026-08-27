from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A support-free, bore-up replacement knob for a D-shaped valve stem.

    shaft_diameter: measured full diameter of the valve stem
    shaft_across_flat: measured distance from the stem flat to its round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if not 0.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be greater than zero and smaller than shaft_diameter",
            param="shaft_across_flat",
        )

    knob_height = 15.0
    knob_depth = 29.0
    grip_extension = 4.5
    grip_radius = knob_depth / 2.0

    center = Box(
        grip_extension * 2.0,
        knob_depth,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    left_lobe = Cylinder(
        grip_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((-grip_extension, 0.0, 0.0))
    right_lobe = Cylinder(
        grip_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((grip_extension, 0.0, 0.0))
    body = (center + left_lobe + right_lobe).clean()

    # A 0.6 mm diametral / across-flat allowance clears the 0.3 mm fit probe,
    # while retaining enough of the flat to reject rotation and a 1.0 mm probe.
    fit_allowance = 0.6
    bore_diameter = shaft_diameter + fit_allowance
    bore_across_flat = shaft_across_flat + fit_allowance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = -bore_radius + bore_across_flat
    bore_floor = 2.5
    cutter_height = knob_height - bore_floor + 0.5

    round_cutter = Cylinder(
        bore_radius,
        cutter_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, bore_floor))
    flat_clip = Box(
        bore_diameter + 1.0,
        bore_diameter + 1.0,
        cutter_height,
        align=(Align.MAX, Align.CENTER, Align.MIN),
    ).translate((bore_flat_x, 0.0, bore_floor))
    bore = (round_cutter & flat_clip).clean()
    body = (body - bore).clean()

    if draft:
        return body

    # Polish only the handled outer top rim; the bed and fit-critical bore stay exact.
    outer_top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > knob_height - 0.01
        and max(
            abs(edge.bounding_box().min.X),
            abs(edge.bounding_box().max.X),
            abs(edge.bounding_box().min.Y),
            abs(edge.bounding_box().max.Y),
        )
        > 10.0
    )
    return polish(body, outer_top_edges, 1.0)
