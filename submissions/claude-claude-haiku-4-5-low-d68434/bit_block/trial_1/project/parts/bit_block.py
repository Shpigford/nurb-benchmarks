from nurb import *
from build123d import Location

@part
def bit_block(shank_diameter=6.0, columns=5):
    """Block holding driver bits upright in a grid.

    shank_diameter: diameter of the bit shanks in mm
    columns: number of pocket columns
    """
    pocket_dia = shank_diameter + 0.3
    rows = 2
    grid_pitch = 8.3
    margin = 2.0
    pocket_depth = 12.0
    floor_thickness = 3.0
    total_height = 15.0

    # Calculate block dimensions from grid parameters
    block_width = margin + pocket_dia/2 + (columns - 1) * grid_pitch + pocket_dia/2 + margin
    block_depth = margin + pocket_dia/2 + (rows - 1) * grid_pitch + pocket_dia/2 + margin

    # Create base block
    block = Box(block_width, block_depth, total_height)

    # Subtract cylindrical pockets at grid positions
    result = block
    for col in range(columns):
        for row in range(rows):
            x = margin + pocket_dia/2 + col * grid_pitch
            y = margin + pocket_dia/2 + row * grid_pitch

            pocket = Cylinder(pocket_dia/2, pocket_depth)
            pocket = pocket.locate(Location((x, y, floor_thickness)))

            result = result - pocket

    # Chamfer top edges (outer perimeter and pocket mouths)
    top_edges = result.edges().filter_by(lambda e: e.bounding_box().min.Z > total_height - 0.5)

    if len(top_edges) > 0:
        result = polish(result, top_edges, 0.8)

    return result
