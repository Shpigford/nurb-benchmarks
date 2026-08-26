from nurb import *

@part
def cable_clip(bundle_diameter=8.0):
    """Screw-down cable clip that holds a cable bundle.

    bundle_diameter: Diameter of the cable bundle to hold (mm)
    """
    # Derived dimensions from bundle_diameter
    channel_width = bundle_diameter + 0.4  # 8.4 mm for 8.0 mm bundle
    channel_depth = bundle_diameter  # 8.0 mm for 8.0 mm bundle
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length_y = 12.0
    tab_length_x = 10.0
    hole_diameter = 4.2

    # Overall dimensions
    total_x = wall_thickness + channel_width + wall_thickness + tab_length_x  # 23.2
    total_z = base_thickness + channel_depth  # 11.0

    # Base plate (Z from 0 to 3.0) - positioned at origin corner
    base = Box(total_x, part_length_y, base_thickness)
    base = base.locate(Location((total_x/2, part_length_y/2, base_thickness/2), (0, 0, 0)))

    # Left wall (Z from 3.0 to 11.0)
    left_wall = Box(wall_thickness, part_length_y, channel_depth)
    left_wall = left_wall.locate(Location((wall_thickness/2, part_length_y/2, base_thickness + channel_depth/2), (0, 0, 0)))

    # Right wall (Z from 3.0 to 11.0)
    right_wall_x_start = wall_thickness + channel_width
    right_wall = Box(wall_thickness, part_length_y, channel_depth)
    right_wall = right_wall.locate(Location((right_wall_x_start + wall_thickness/2, part_length_y/2, base_thickness + channel_depth/2), (0, 0, 0)))

    # Combine base and walls into one solid
    clip = base.fuse(left_wall).fuse(right_wall)

    # Mounting hole in the tab
    hole_x = right_wall_x_start + wall_thickness + tab_length_x / 2  # 18.2
    hole_y = part_length_y / 2  # 6.0
    hole_radius = hole_diameter / 2  # 2.1

    # Hole goes through the tab (Z from 0 to 3.0)
    hole = Cylinder(hole_radius, base_thickness)
    hole = hole.locate(Location((hole_x, hole_y, base_thickness/2), (0, 0, 0)))

    # Subtract the hole
    clip = clip.cut(hole)

    return clip
