from nurb import *

@part
def cable_clip(bundle_diameter: float = 8.0, draft: bool = False):
    """Screw-down cable clip for cable bundles.

    bundle_diameter: diameter of cable bundle to hold (mm)
    """

    # Dimensions derived from bundle diameter
    inner_width = bundle_diameter + 0.4
    inner_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0
    channel_length = 12.0
    tab_length = 10.0
    hole_diameter = 4.2

    # Calculate outer dimensions
    outer_width = inner_width + 2 * wall_thickness
    total_height = base_thickness + inner_depth

    # Create main channel body
    # Box is centered at origin, so position appropriately
    # Channel block from X=-outer_width/2 to outer_width/2, Y=-channel_length/2 to channel_length/2, Z=0 to total_height
    channel_box = Box(outer_width, channel_length, total_height)
    channel_box = channel_box.translate((0, 0, total_height / 2))

    # Channel void (the opening where cable goes)
    # Positioned in the center of the channel, from Z=base_thickness to base_thickness+inner_depth
    channel_void = Box(inner_width, channel_length, inner_depth)
    channel_void = channel_void.translate((0, 0, base_thickness + inner_depth / 2))

    channel_body = channel_box - channel_void

    # Create mounting tab extending from the right side of the channel
    # Tab goes from X=outer_width/2 to X=outer_width/2+tab_length
    tab_block = Box(tab_length, channel_length, base_thickness)
    tab_block = tab_block.translate((outer_width / 2 + tab_length / 2, 0, base_thickness / 2))

    # Create through-hole in tab, centered in the tab
    hole = Cylinder(hole_diameter / 2, base_thickness)
    hole = hole.translate((outer_width / 2 + tab_length / 2, 0, base_thickness / 2))

    # Combine all parts
    result = channel_body + tab_block - hole

    if not draft:
        # Polish tab and outer edges, but not channel opening edges which create slivers
        bed_level = result.bounding_box().min.Z
        concave = concave_edges(result)

        # Identify edges at the top of the part (channel opening edges)
        # and exclude them to avoid creating slivers
        top_z = result.bounding_box().max.Z
        all_edges = result.edges()

        edges_to_polish = [e for e in all_edges
                          if (e.bounding_box().min.Z > bed_level and  # Not on bed
                              e not in concave and  # Not concave (internal channel)
                              e.bounding_box().max.Z < top_z)]  # Not at very top

        if edges_to_polish:
            result = polish(result, edges_to_polish, 0.3)

    return result
