from math import sqrt

from nurb import *

# M4 pan-head through the wall: medium clearance, driver/head envelope from the brief.
_SCREW_HOLE = 4.4
_DRIVER = 8.4
_SEAT_DEPTH = 2.4
_BUNDLE_CLEARANCE = 0.4


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that carries a horizontal cable bundle on one M4 pan-head screw.

    bundle_diameter: measured width of the taped cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            "bundle_diameter 4mm is the smallest this clip can still wrap",
            param="bundle_diameter",
        )

    inner = bundle_diameter + _BUNDLE_CLEARANCE
    back_t = _SEAT_DEPTH + 0.6
    floor_t = 2.4
    front_t = 2.4
    length = 12.0
    hole_r = _SCREW_HOLE / 2.0
    driver_r = _DRIVER / 2.0
    lip_h = floor_t + inner
    # Keep the 8.4 driver cylinder above the front lip, and the head above the bundle.
    screw_z = lip_h + driver_r + 2.5
    teardrop_peak = hole_r * sqrt(2.0)
    plate_h = screw_z + teardrop_peak + 2.6

    # 1mm outer chamfers and 1.5mm inner corners live in the profile so the
    # Y-end faces never grow the three-chamfer sliver triangles polish leaves.
    # 3mm inner chamfers would cut the 8.4mm bundle seat on this size of clip.
    c = 1.0
    s = 1.5
    x_front = back_t + inner + front_t
    x_lip = back_t + inner
    profile = Plane.XZ * Polygon(
        (0.0, 0.0),
        (x_front, 0.0),
        (x_front, lip_h - c),
        (x_front - c, lip_h),
        (x_lip + c, lip_h),
        (x_lip, lip_h - c),
        (x_lip, floor_t + s),
        (x_lip - s, floor_t),
        (back_t + s, floor_t),
        (back_t, floor_t + s),
        (back_t, plate_h - c),
        (back_t - c, plate_h),
        (0.0, plate_h),
    )
    body = extrude(profile, amount=-length)

    s45 = hole_r * sqrt(2.0) / 2.0
    tear = Circle(hole_r) + Polygon(
        (s45, s45),
        (0.0, teardrop_peak),
        (-s45, s45),
    )
    hole = extrude(
        Plane.YZ.offset(-1.0) * Pos(length / 2.0, screw_z) * tear,
        amount=back_t + 2.0,
    )
    body = body - hole

    if draft:
        return body

    # Chamfers already live in the XZ profile. A second polish pass on the Y-end
    # corners makes the sub-1mm2 triangles the sliver check rejects.
    return body
