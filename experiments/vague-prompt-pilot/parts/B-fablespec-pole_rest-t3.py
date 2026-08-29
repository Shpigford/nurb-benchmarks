from nurb import *

CENTER_HEIGHT = 18.0
FIT_CLEARANCE = 0.3
BLOCK_Y = 12.0
BLOCK_H = 22.0
BLOCK_X_MIN = 30.0
MIN_WALL = 4.0
LEAD_IN = 1.5


@part
def pole_rest(pole_d=measured("pole_diameter"), draft=False):
    """Bench rest that cradles a wet-finish pole for drying.

    pole_d: diameter of the pole this rest holds.
    """
    R = pole_d / 2 + FIT_CLEARANCE
    slot_z = CENTER_HEIGHT + FIT_CLEARANCE
    slot_bottom = CENTER_HEIGHT - pole_d / 2
    block_x = max(BLOCK_X_MIN, 2 * R + 2 * MIN_WALL)

    if slot_bottom < 8.0 - 1e-9:
        reject(
            f"slot bottom at {slot_bottom:.2f} mm leaves under 8 mm of plastic under the pole",
            param="pole_d",
        )
    if slot_z + R <= BLOCK_H:
        reject(
            "slot does not open through the top face; pole cannot drop in from above",
            param="pole_d",
        )

    block = Box(block_x, BLOCK_Y, BLOCK_H)
    block = block.move(Location((0, 0, BLOCK_H / 2)))

    extra = 2.0
    cylinder = Cylinder(R, BLOCK_Y + extra)
    cylinder = cylinder.rotate(Axis.X, 90)
    cylinder = cylinder.move(Location((0, 0, slot_z)))

    wall_h = BLOCK_H - slot_z + extra
    channel = Box(2 * R, BLOCK_Y + extra, wall_h)
    channel = channel.move(Location((0, 0, slot_z + wall_h / 2)))

    slot = cylinder + channel
    body = block - slot

    if abs((slot_bottom + pole_d / 2) - CENTER_HEIGHT) > 1e-9:
        reject("pole center height is not 18.0 mm")
    if abs(2 * R - (pole_d + 2 * FIT_CLEARANCE)) > 1e-9:
        reject("slot gap is not pole_d + 2 × fit_clearance")

    if draft:
        return body

    top = BLOCK_H
    lead = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 0.05
        and abs(e.bounding_box().max.Z - top) < 0.05
        and abs(abs(e.center().X) - R) < 0.05
        and e.length > BLOCK_Y * 0.8
    )
    if len(lead) != 2:
        reject(f"expected 2 slot lead-in edges, found {len(lead)}")
    return chamfer(lead, LEAD_IN)
