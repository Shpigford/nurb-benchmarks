"""Single-screw wall holder for a cable bundle running along Y."""

from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall-mounted cable-bundle holder, printed flat with its back at minimum X.

    bundle_diameter: measured diameter of the cable bundle that passes along Y
    draft: skip the cosmetic edge polish for fast previews
    """
    # The opening is deliberately wider than the bundle by 0.8 mm overall.
    bundle_clearance = 0.8
    opening = bundle_diameter + bundle_clearance

    length = 16.0
    half_length = length / 2.0
    back_thickness = 2.8
    back_height = 20.0
    floor_thickness = 3.0
    floor_width = back_thickness + opening + 2.2
    rail_thickness = 2.2
    rail_height = 12.0

    # The bundle sits 0.4 mm above the floor.  The front rails then catch a
    # one-millimetre +X move while the floor catches a one-millimetre -Z move.
    bundle_bottom = floor_thickness + 0.4
    bundle_center_z = bundle_bottom + bundle_diameter / 2.0

    back = Pos(0, -half_length, 0) * Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Pos(0, -half_length, 0) * Box(
        floor_width,
        length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Keep the center of the screw clear of the 8.4 mm head-and-driver
    # cylinder.  Each rail is 3.4 mm long, so the two rails retain well over
    # one third of the bundle's full-length path.
    head_radius = 4.2
    rail_gap_half = head_radius + 0.4
    rail_end_length = half_length - rail_gap_half
    rail_x = floor_width - rail_thickness
    lower_rail = Pos(rail_x, -half_length, 0) * Box(
        rail_thickness,
        rail_end_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    upper_rail = Pos(rail_x, rail_gap_half, 0) * Box(
        rail_thickness,
        rail_end_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Polish only the free top edges of the back plate before joining the
    # grounded retention features.  Keeping the floor/rail junctions sharp
    # avoids cosmetic chamfers in structural inside corners and prevents
    # tiny corner faces at the rail ends.
    if not draft:
        bed = back.bounding_box().min.Z
        back_edges = back.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > bed + 0.01
        )
        back = polish(back, back_edges, 1.0)

    body = back + floor + lower_rail + upper_rail

    # M4 medium clearance, through the 2.8 mm back plate.  The hole is high
    # enough that the installed head clears the retained bundle vertically.
    screw_hole_diameter = 4.4
    screw_z = 16.0
    screw_hole = Pos(-0.1, 0, screw_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole_diameter / 2.0,
        back_thickness + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - screw_hole

    return body
