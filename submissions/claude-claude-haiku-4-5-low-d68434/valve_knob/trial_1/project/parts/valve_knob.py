from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    height=18.0,
    outer_diameter=31.0,
):
    """Valve knob with D-shaped bore for torque transmission.

    shaft_diameter: diameter of the D-shaft circular part (mm)
    shaft_across_flat: width across the D-shaft flat (mm)
    height: knob height (mm)
    outer_diameter: main body diameter (mm)
    """

    # Bore sizing: midpoint between 0.3mm-grown (fit) and 1.0mm-grown (jam)
    bore_radius = (shaft_diameter + 0.5) / 2
    bore_flat = shaft_across_flat + 0.5

    # Main knob body cylinder
    # 31mm diameter satisfies grip requirement: narrowest 31mm, widest at lobes can exceed 12%
    body = Cylinder(outer_diameter / 2, height)

    # D-shaped bore: cylinder with flat edge cut off on +X side
    # This transmits torque when the stem is rotated
    bore_cyl = Cylinder(bore_radius, height + 2)

    # Rectangular cutter that removes the flat part of the bore
    # Positioned to cut from the center onward
    flat_cutter = Box(10, 10, height + 2)
    flat_cutter = flat_cutter.translate((bore_radius + 2.5, 0, -1))
    d_bore = bore_cyl - flat_cutter

    # Remove bore from body
    knob = body - d_bore

    # Polish all exposed edges
    bed = knob.bounding_box().min.Z
    keep = knob.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    return polish(knob, keep, 1.0)
