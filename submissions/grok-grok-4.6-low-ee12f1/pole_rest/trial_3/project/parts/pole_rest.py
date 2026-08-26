from nurb import *

AXIS_HEIGHT = 18.0
CLEARANCE = 0.2
BACKING = 1.6
LENGTH = 24.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """Cradle a freshly finished pole while it dries.

    pole_diameter: width of the pole across; the seat is cut from this
    """
    pole_diameter = float(pole_diameter)
    if pole_diameter < 10.0:
        reject(
            "pole_diameter under 10mm leaves no bed under the cradle: raise it",
            param="pole_diameter",
        )
    if pole_diameter / 2.0 + CLEARANCE >= AXIS_HEIGHT - 3.0:
        reject(
            "pole_diameter is too large for an 18mm axis height: lower it",
            param="pole_diameter",
        )

    inner_r = pole_diameter / 2.0 + CLEARANCE
    width = 2.0 * (inner_r + BACKING + 1.0)
    height = AXIS_HEIGHT - 1.0

    body = Box(width, LENGTH, height)
    body = body.move(Location((0, 0, height / 2.0)))

    trough = Cylinder(inner_r, LENGTH + 8.0)
    trough = trough.rotate(Axis.X, 90.0)
    trough = trough.move(Location((0, 0, AXIS_HEIGHT)))

    # Chute starts above the 120° cradle so the pole can drop in along -Z.
    slot_w = pole_diameter + 2.0 * CLEARANCE
    slot_bottom = AXIS_HEIGHT - inner_r * 0.40
    slot_h = 40.0
    slot = Box(slot_w, LENGTH + 8.0, slot_h)
    slot = slot.move(Location((0, 0, slot_bottom + slot_h / 2.0)))

    body = body - trough - slot

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05 and e.length > 8.0
    )
    concave = set(concave_edges(body))
    keep = keep.filter_by(lambda e: e not in concave)
    return polish(body, keep, 1.0)
