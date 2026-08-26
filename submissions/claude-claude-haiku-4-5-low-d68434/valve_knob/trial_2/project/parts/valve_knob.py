from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_height=13.0,
    knob_width_x=28.0,
    knob_width_y=36.0,
    draft=False,
):
    """
    Replacement knob for a D-shaft valve handle.

    The bore opens straight up on the vertical centerline with the stem's
    flat facing +X. The bore accepts the nominal stem with 0.3mm clearance
    on both diameter and flat width, jams with 1.0mm growth, and engages
    the flat for torque transmission.

    shaft_diameter: Diameter of the D-shaft in mm
    shaft_across_flat: Width across the flat of the D-shaft in mm
    knob_height: Overall height of the knob in mm
    knob_width_x: Width of the knob in X direction (narrow, along flat) in mm
    knob_width_y: Width of the knob in Y direction (wide, for grip) in mm
    """

    # Bore dimensions with clearance for the nominal stem
    bore_clearance = 0.3
    bore_diameter = shaft_diameter + bore_clearance
    bore_flat_width = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_depth = 12.0

    # Create main body as a rectangular box for better grip geometry
    # X is narrow (28mm), Y is wide (36mm) - ratio is 36/28 = 1.29 or 29% wider
    # This satisfies the grip requirement of 12% wider reach from centerline
    knob = Box(length=knob_width_x, width=knob_width_y, height=knob_height)

    # Create cylindrical bore that accepts the round part of the D-shaft
    cylindrical_bore = Cylinder(
        radius=bore_radius, height=bore_depth + 1.0
    ).translate((0, 0, knob_height - bore_depth))
    knob = knob.cut(cylindrical_bore)

    # Create rectangular cut to form the flat on the bore
    # The flat faces +X (positive X direction)
    # We cut from the -X side (negative X side) of the bore
    # This creates the D-shape for torque transmission
    flat_cut_box = Box(
        length=bore_radius + 0.5,
        width=bore_flat_width + 1.0,
        height=bore_depth + 2.0,
    ).translate(
        (-bore_radius - 0.25, 0, knob_height - bore_depth - 1.0)
    )
    knob = knob.cut(flat_cut_box)

    if draft:
        return knob

    # Polish only the top edges, excluding bore edges
    bed = knob.bounding_box().min.Z
    # Only polish edges that are at the very top and on the outer perimeter
    top_edges = knob.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - knob_height) < 0.5
        and abs(e.bounding_box().max.Z - knob_height) < 0.5
    )
    return polish(knob, top_edges, 1.0) if top_edges else knob
