from nurb import *


@part
def pole_rest(pole_diameter=20.0):
    """Cradle for holding a pole while finish dries.

    pole_diameter: diameter of the pole (mm)
    """

    # Pole geometry from spec
    pole_radius = pole_diameter / 2
    pole_axis_height = 18.0

    # Cradle support requirements
    clearance = 0.1  # Minimum clear distance from pole
    contact_zone = 0.4  # Thickness of contact material
    backing = 1.2  # Material thickness behind contact

    # Calculated radii for the cradle
    cavity_radius = pole_radius + clearance  # Inner cavity radius (10.1 mm)
    support_outer_radius = cavity_radius + contact_zone + backing  # Outer radius (11.6 mm)

    # Pole lowest point and base height
    pole_lowest_z = pole_axis_height - pole_radius  # 8.0 mm
    base_height = pole_lowest_z + 1.0  # Extend slightly above lowest point for support

    # Create solid base block
    base = Box(30, 30, base_height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Carve out the inner cavity (where pole sits)
    # Only remove from the top half to create semicircular support
    cavity = Cylinder(cavity_radius, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
        Location(Pos(0, 0, pole_lowest_z - 0.5))
    )

    # Cut cavity to keep only upper half (so bottom arc provides support)
    cavity_cut = Box(60, 30, cavity_radius + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
        Location(Pos(0, 0, pole_lowest_z - cavity_radius))
    )

    cavity_to_remove = cavity & cavity_cut

    # Create the finished cradle by subtracting the cavity
    rest = base - cavity_to_remove

    # Polish edges for finish and printability
    bed = rest.bounding_box().min.Z
    keep = rest.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    rest = polish(rest, keep, 0.5)

    return rest
