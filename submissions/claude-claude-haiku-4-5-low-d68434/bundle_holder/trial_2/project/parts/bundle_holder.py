from nurb import *

@part
def bundle_holder(bundle_diameter=8.0):
    """Wall-mounted cable bundle holder

    bundle_diameter: diameter of the cable bundle to hold (mm)
    """

    # Design parameters
    clearance = 0.4
    pocket_width = bundle_diameter + clearance  # 8.4mm
    wall_thick = 0.8

    # Dimensions (back face area = length × height, must be >100mm²)
    holder_length = 15.0  # Y: 15mm
    back_depth = 3.0  # X: mounting surface depth
    cradle_depth = 5.5  # X: cradle extends this far
    holder_height = 10.0  # Z: 10mm, gives 15×10=150mm² minus bore ~100mm²

    # Back plate (mounting surface against wall)
    back = Box(back_depth, holder_length, holder_height)
    back = back.translate((back_depth / 2, 0, holder_height / 2))

    # Floor/base platform
    floor = Box(back_depth + cradle_depth, holder_length, wall_thick)
    floor = floor.translate((
        (back_depth + cradle_depth) / 2,
        0,
        wall_thick / 2
    ))

    # Tall cradle foundation (supports all cradle elements)
    # Extends full height from floor to accommodate all parts
    cradle_foundation = Box(
        cradle_depth - 0.2,
        holder_length,
        holder_height - 1.0
    )
    cradle_foundation = cradle_foundation.translate((
        back_depth + (cradle_depth - 0.2) / 2,
        0,
        wall_thick + (holder_height - 1.0) / 2
    ))

    # Pocket floor (carved into foundation)
    pocket_floor = Box(
        cradle_depth - 1.0,
        holder_length - 2.5,
        wall_thick
    )
    pocket_floor = pocket_floor.translate((
        back_depth + (cradle_depth - 1.0) / 2,
        0,
        wall_thick + 1.0
    ))

    # Front blocker wall
    front_height = pocket_width + 1.2
    front = Box(wall_thick + 0.2, holder_length - 2.0, front_height)
    front = front.translate((
        back_depth + cradle_depth - 0.5,
        0,
        wall_thick + 1.0 + front_height / 2
    ))

    # Combine: back plate, floor, foundation, pocket floor, and front
    holder = back + floor + cradle_foundation + pocket_floor + front

    # Create mounting bore
    bore = Cylinder(4.4 / 2, back_depth + 0.5)
    bore = bore.rotate(Axis.Y, 90)
    bore = bore.translate((0, 0, holder_height / 2))

    holder = holder - bore

    # Polish edges
    all_edges = holder.edges()
    holder = polish(holder, all_edges, 0.5)

    return holder
