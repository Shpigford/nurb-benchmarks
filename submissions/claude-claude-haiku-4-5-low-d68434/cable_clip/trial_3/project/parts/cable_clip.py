from nurb import *

@part
def cable_clip(bundle_diameter: float = 8.0):
    """Cable clip with parametric open-top channel.

    bundle_diameter: cable bundle diameter in mm
    """

    # Channel dimensions derived from bundle_diameter
    inner_width = bundle_diameter + 0.4
    inner_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0

    # Part dimensions
    length_y = 12.0
    tab_length_x = 10.0
    hole_diameter = 4.2

    # Computed overall dimensions
    outer_width = inner_width + 2 * wall_thickness
    total_width = outer_width + tab_length_x
    total_height = base_thickness + inner_depth

    # Create the overall bounding box
    body = Box(total_width, length_y, total_height)

    # Cut away the tab part from above the base (keep only the channel area high)
    tab_cutout = Box(tab_length_x, length_y, inner_depth)
    tab_cutout = tab_cutout.translate((outer_width, 0, base_thickness))
    body = body - tab_cutout

    # Cut the channel interior (open-top channel)
    cavity = Box(inner_width, length_y, inner_depth)
    cavity = cavity.translate((wall_thickness, 0, base_thickness))
    body = body - cavity

    # Cut hole in mounting tab
    hole = Cylinder(hole_diameter / 2, base_thickness)
    hole = hole.translate((outer_width + tab_length_x / 2, length_y / 2, 0))
    body = body - hole

    return body
