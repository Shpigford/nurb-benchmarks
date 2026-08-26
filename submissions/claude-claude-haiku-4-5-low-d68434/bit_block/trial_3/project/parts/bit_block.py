from nurb import *


@part
def bit_block(shank_diameter=6.0, columns=5):
    """
    Bench block holding driver bits upright in a grid of round pockets.

    shank_diameter: Diameter of driver bit shanks (mm)
    columns: Number of columns in the pocket grid
    """
    # Derived measurements
    pocket_diameter = shank_diameter + 0.3
    pocket_depth = 12.0
    floor_thickness = 3.0
    block_height = 15.0
    grid_pitch = 8.3
    edge_margin = 2.0
    chamfer_size = 0.8
    rows = 2

    pocket_radius = pocket_diameter / 2

    # Calculate block dimensions
    block_width = 2 * (pocket_radius + edge_margin) + (columns - 1) * grid_pitch
    block_depth = 2 * (pocket_radius + edge_margin) + (rows - 1) * grid_pitch

    # Create base block
    part = Box(block_width, block_depth, block_height)

    # Calculate pocket center z-position (relative to block center at origin)
    # Block spans from -block_height/2 to block_height/2
    # Pockets start at floor_thickness above the bottom
    pocket_center_z = -block_height/2 + floor_thickness + pocket_depth/2

    # Cut pockets in grid
    for col in range(columns):
        for row in range(rows):
            # Calculate pocket center position
            pocket_x = -block_width/2 + pocket_radius + edge_margin + col * grid_pitch
            pocket_y = -block_depth/2 + pocket_radius + edge_margin + row * grid_pitch

            # Create pocket cylinder with exact depth
            pocket = Cylinder(pocket_radius, pocket_depth)
            pocket = pocket.translate([pocket_x, pocket_y, pocket_center_z])

            part = part.cut(pocket)

    # Add pocket mouth chamfers by subtracting very thin disks at pocket openings
    top_z = block_height / 2

    # For each pocket, subtract a thin ring at the edge to create the lead-in chamfer
    for col in range(columns):
        for row in range(rows):
            px = -block_width/2 + pocket_radius + edge_margin + col * grid_pitch
            py = -block_depth/2 + pocket_radius + edge_margin + row * grid_pitch

            # Subtract a very thin disk that's positioned to create a small beveled lip
            # at the pocket opening edge
            chamfer_disk = Cylinder(pocket_radius + chamfer_size * 0.3, chamfer_size * 0.2)
            chamfer_disk = chamfer_disk.translate([px, py, top_z - chamfer_size * 0.1])
            part = part.cut(chamfer_disk)

    # Add chamfers to top outer perimeter by subtracting small boxes at edges
    # Subtract from the top 4 edges where the outer faces meet the top surface
    edge_chamfer = chamfer_size * 0.4
    edge_length = block_width + block_depth  # approximate for sweeping along edges

    # Top edge along X direction (at +Y face edge)
    wedge = Box(block_width + chamfer_size, edge_chamfer, edge_chamfer)
    wedge = wedge.translate([0, block_depth/2, top_z])
    part = part.cut(wedge)

    # Bottom edge along X direction (at -Y face edge)
    wedge = Box(block_width + chamfer_size, edge_chamfer, edge_chamfer)
    wedge = wedge.translate([0, -block_depth/2, top_z])
    part = part.cut(wedge)

    # Left edge along Y direction (at -X face edge)
    wedge = Box(edge_chamfer, block_depth + chamfer_size, edge_chamfer)
    wedge = wedge.translate([-block_width/2, 0, top_z])
    part = part.cut(wedge)

    # Right edge along Y direction (at +X face edge)
    wedge = Box(edge_chamfer, block_depth + chamfer_size, edge_chamfer)
    wedge = wedge.translate([block_width/2, 0, top_z])
    part = part.cut(wedge)

    return part
