from nurb import *

@part
def bit_block(
    shank_diameter: float = 6.0,
    columns: int = 5,
    rows: int = 2,
):
    """Bench block that holds driver bits upright in a grid.

    shank_diameter: The diameter of the bit's shank (mm).
    columns: Number of columns of pockets.
    rows: Number of rows of pockets.
    """

    # Derived dimensions
    pocket_diameter = shank_diameter + 0.3
    pocket_radius = pocket_diameter / 2

    # Constants from requirements
    grid_pitch = 8.3
    margin = 2.0
    chamfer_size = 0.8
    floor_height = 3.0
    pocket_depth = 12.0
    total_height = 15.0

    # Calculate block dimensions from grid geometry
    # Width: margin + radius + (columns-1)*pitch + radius + margin
    block_width = margin + pocket_radius + (columns - 1) * grid_pitch + pocket_radius + margin
    # Depth: margin + radius + (rows-1)*pitch + radius + margin
    block_depth = margin + pocket_radius + (rows - 1) * grid_pitch + pocket_radius + margin
    block_height = total_height

    # Create base block
    block = Box(block_width, block_depth, block_height)

    # Subtract pockets in a grid
    for col in range(columns):
        for row in range(rows):
            # Pocket XY position (center of pocket opening)
            pocket_x = margin + pocket_radius + col * grid_pitch
            pocket_y = margin + pocket_radius + row * grid_pitch
            # Pocket bottom Z: at floor_height (3.0mm from block bottom)
            pocket_z = floor_height

            # Create cylindrical pocket (extends upward from floor_height)
            pocket = Cylinder(pocket_radius, pocket_depth)
            # Position it so its base is at floor_height
            pocket = pocket.translate((pocket_x, pocket_y, pocket_z))
            block = block - pocket

    # Chamfer pocket rims (concave edges where pockets open to the top)
    concave = concave_edges(block)
    if concave:
        block = chamfer(concave, chamfer_size)

    # Chamfer top outer perimeter edges
    # Find all faces and identify the top faces (those pointing mostly upward)
    top_perimeter_edges = []
    try:
        for face in block.faces:
            # Top faces have normal pointing up (z component > 0.5)
            if hasattr(face, 'normal_direction') and face.normal_direction.z > 0.5:
                # Get all edges of this top face
                for edge in face.edges:
                    # Skip concave edges (already chamfered)
                    if edge not in (concave or []):
                        # Check if this edge is on the perimeter
                        # An edge on the perimeter connects the top face to a side face
                        adjacent_faces = [f for f in block.faces if edge in (f.edges if hasattr(f, 'edges') else [])]
                        if len(adjacent_faces) >= 2:
                            top_perimeter_edges.append(edge)
    except:
        pass

    # Chamfer the top perimeter edges
    if top_perimeter_edges:
        # Remove duplicates
        top_perimeter_edges = list(set(top_perimeter_edges))
        block = polish(block, top_perimeter_edges, chamfer_size)

    return block
