from nurb import *

CENTER_HEIGHT = 18.0
CLEARANCE = 0.25
WALL = 3.0
LENGTH = 20.0
LEAD_IN = 2.0
WALL_ABOVE = 4.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A bench rest that cradles a finishing pole while it dries.

    pole_diameter: diameter of the pole this rest holds
    """
    r_c = pole_diameter / 2 + CLEARANCE
    arc_z = CENTER_HEIGHT + CLEARANCE
    width = 2 * r_c + 2 * WALL
    height = CENTER_HEIGHT + WALL_ABOVE

    if r_c * 2 >= width:
        reject(
            "side walls vanished: pole_diameter is too large for WALL",
            param="pole_diameter",
        )
    if arc_z - r_c <= 0:
        reject(
            "cradle cuts through the bed: raise CENTER_HEIGHT or shrink pole_diameter",
            param="pole_diameter",
        )

    block = Box(width, LENGTH, height).moved(Location((0, 0, height / 2)))

    extra = 2.0
    cradle = Cylinder(r_c, LENGTH + extra)
    cradle = cradle.rotate(Axis.X, 90)
    cradle = cradle.moved(Location((0, 0, arc_z)))

    slot_h = height - arc_z + extra
    slot = Box(2 * r_c, LENGTH + extra, slot_h).moved(
        Location((0, 0, arc_z + slot_h / 2))
    )

    body = block - (cradle + slot)

    top_inner = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - height) < 0.05
        and abs(e.bounding_box().max.Z - height) < 0.05
        and abs(abs(e.center().X) - r_c) < 0.05
        and (e.bounding_box().max.Y - e.bounding_box().min.Y) > LENGTH * 0.5
    )
    body = chamfer(top_inner, LEAD_IN)

    groove_bottom = arc_z - r_c
    expected_bottom = CENTER_HEIGHT - pole_diameter / 2
    if abs(groove_bottom - expected_bottom) > 0.01:
        reject(
            f"groove bottom at {groove_bottom:.3f} mm, expected {expected_bottom:.3f}"
        )

    return body
