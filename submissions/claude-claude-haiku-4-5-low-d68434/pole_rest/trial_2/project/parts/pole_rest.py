from nurb import *


@part
def pole_rest(pole_diameter=20.0, draft=False):
    """Rest for holding a drying pole in a cradle.

    pole_diameter: diameter of the pole to be cradled, in mm
    """
    # Fixed requirements
    axis_height = 18.0
    clearance = 0.1
    min_support_thickness = 1.2

    # Derived geometry
    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + clearance

    # Base dimensions
    # Width (X): needs to support the cradle (radius 10.1) with minimum backing (1.2mm)
    # So minimum width is 2*(10.1+1.2) ≈ 22.6mm. Use 25mm with margin.
    base_width = 25.0
    # Length (Y) must be at least 20mm per requirements
    base_length = 25.0
    # Height: from bed (Z=0) to where the cradle top begins
    # Cradle top is at: axis_height - cradle_radius
    base_height = axis_height - cradle_radius

    # Create the main base block
    base = Box(base_width, base_length, base_height)

    # Create the cylindrical void for the cradle
    # Create a cylinder along Z, then rotate it to align with Y
    # The cylinder needs to be positioned so its axis is at (0, 0, axis_height)
    void = Cylinder(
        cradle_radius,
        base_length,
        rotation=(90, 0, 0)  # Rotate 90° around X to align cylinder with Y
    )
    # Move the cylinder to the right position
    void = void.locate(Location((0, 0, axis_height)))

    # Subtract the void from the base to create the cradle
    part = base - void

    if draft:
        return part

    # Polish edges except the bed
    bed = part.bounding_box().min.Z
    keep = part.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    return polish(part, keep, 1.0)
