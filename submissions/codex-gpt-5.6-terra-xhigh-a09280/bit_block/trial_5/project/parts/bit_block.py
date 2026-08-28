from nurb import *


@part
def bit_block(shank_diameter: float = 6.0, columns: int = 5):
    """A compact upright holder for driver bits.

    shank_diameter: measured width across each bit shank.
    columns: number of bit pockets across the block.
    """
    clearance = 0.3
    pocket_diameter = shank_diameter + clearance
    pocket_radius = pocket_diameter / 2
    pocket_depth = 12.0
    floor_thickness = 3.0
    side_wall = 2.0
    pitch = pocket_diameter + side_wall
    length = (columns - 1) * pitch + pocket_diameter + 2 * side_wall
    width = pitch + pocket_diameter + 2 * side_wall
    height = floor_thickness + pocket_depth

    body = Box(length, width, height)

    # Only the original top perimeter is softened; the bed perimeter remains sharp.
    top = body.bounding_box().max.Z
    top_perimeter = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z == top
    )
    body = polish(body, top_perimeter, 0.8)

    first_x = -length / 2 + side_wall + pocket_radius
    first_y = -width / 2 + side_wall + pocket_radius
    pocket_center_z = -height / 2 + floor_thickness + pocket_depth / 2
    for column in range(columns):
        for row in range(2):
            x = first_x + column * pitch
            y = first_y + row * pitch
            pocket = Cylinder(pocket_radius, pocket_depth).translate(
                (x, y, pocket_center_z)
            )
            # Cone is bottom-radius then top-radius: this removes a true 0.8 mm,
            # 45-degree lead-in without changing the 6.3 mm straight bore.
            lead_in = Cone(pocket_radius, pocket_radius + 0.8, 0.8).translate(
                (x, y, height / 2 - 0.4)
            )
            body = body.cut(pocket.fuse(lead_in))

    return body
