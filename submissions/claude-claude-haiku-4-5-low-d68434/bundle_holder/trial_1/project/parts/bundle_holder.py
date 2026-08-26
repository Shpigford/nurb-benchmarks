from nurb import *

@part
def bundle_holder(bundle_diameter=8.0):
    """Wall-mounted cable bundle holder.

    Mounts to wall with M4 screw, holds cable bundle running horizontally.

    bundle_diameter: diameter of the cable bundle in mm
    """

    bd = bundle_diameter
    clearance = 0.4
    screw_hole_dia = 4.4
    screw_hole_r = screw_hole_dia / 2

    # Dimensions
    back_thickness = 1.0  # Material at the back (X=0)
    wall_thickness = 1.0  # Thickness of side supports
    floor_height = 1.0    # Thickness of bottom support

    base_length = 22  # Along Y axis
    base_height = 5   # Along Z axis
    base_depth = 8    # Along X axis

    # Create the main solid
    holder = Box(base_depth, base_length, base_height)

    # Carve out the pocket for the bundle
    # This pocket runs the full length along Y
    pocket_width = bd + clearance * 2
    pocket_height = base_height - floor_height

    pocket = Box(
        base_depth - back_thickness,
        pocket_width,
        pocket_height
    )

    pocket = pocket.translate((
        back_thickness / 2,
        0,
        floor_height / 2
    ))

    holder = holder - pocket

    # Carve out additional material in the center to form better cradle shape
    # and to make side supports visible
    inner_width = pocket_width - wall_thickness * 2
    inner_height = pocket_height - 1.0

    inner_pocket = Box(
        base_depth - back_thickness - 0.5,
        inner_width,
        inner_height
    )

    inner_pocket = inner_pocket.translate((
        back_thickness / 2 + 0.25,
        0,
        floor_height + (inner_height - 1.0) / 2 + 0.5
    ))

    holder = holder - inner_pocket

    # Drill screw hole through X axis
    with BuildSketch(Plane.XZ) as sketch:
        Circle(screw_hole_r)
    screw_hole = extrude(sketch, amount=base_depth)
    holder = holder - screw_hole

    return holder
