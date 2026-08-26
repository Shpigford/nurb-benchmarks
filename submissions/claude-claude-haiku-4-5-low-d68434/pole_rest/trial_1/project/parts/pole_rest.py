from nurb import *

@part
def pole_rest(pole_diameter=20.0, length=40.0, width=25.0, draft=False):
    """Cradle rest for a drying pole.

    pole_diameter: diameter of the pole in mm
    length: cradle length along Y (pole axis direction)
    width: cradle width in X
    """
    pole_radius = pole_diameter / 2
    clearance = 0.1
    support_thickness = 1.2

    # The pole axis is at Z=18, centered at X=0
    # Pole bottom is at Z = 18 - pole_radius = 18 - pole_diameter/2
    pole_bottom = 18.0 - pole_radius

    # Base platform
    base = Box(width, length, 2.0)

    # Build layered bowl-shaped cradle derived from pole geometry
    # Layer 1: bottom support - full width
    layer1_width = width - 1.0
    layer1_height = 3.0
    layer1 = Box(layer1_width, length - 2.0, layer1_height)
    layer1 = layer1.move(Location((0, 0, layer1_height / 2)))

    # Layer 2: narrower middle support
    layer2_width = pole_diameter + 4.0  # Slightly wider than pole
    layer2_height = 3.0
    layer2 = Box(layer2_width, length - 3.0, layer2_height)
    layer2 = layer2.move(Location((0, 0, layer1_height + layer2_height / 2)))

    # Layer 3: narrower top support (cradle surface)
    layer3_width = pole_diameter - 2.0  # Narrower than pole for better cradle
    layer3_height = max(pole_bottom - (layer1_height + layer2_height) - 0.5, 2.0)
    layer3 = Box(layer3_width, length - 4.0, layer3_height)
    layer3 = layer3.move(Location((0, 0, layer1_height + layer2_height + layer3_height / 2)))

    # Side supports for structural integrity
    support_width = 4.0
    support_height = layer1_height + layer2_height - 0.5
    left_support = Box(support_width, length - 2.0, support_height)
    left_support = left_support.move(Location((-(width / 2 - support_width / 2), 0, 1.0 + support_height / 2)))

    right_support = Box(support_width, length - 2.0, support_height)
    right_support = right_support.move(Location(((width / 2 - support_width / 2), 0, 1.0 + support_height / 2)))

    # Combine all parts
    result = base + layer1 + layer2 + layer3 + left_support + right_support

    if draft:
        return result

    return result
