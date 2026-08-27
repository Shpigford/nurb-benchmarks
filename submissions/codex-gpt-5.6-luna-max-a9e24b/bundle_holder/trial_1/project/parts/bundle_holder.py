from nurb import *


@part
def bundle_holder(bundle_diameter=8.0, draft=False):
    """Wall holder for a horizontal cable bundle.

    bundle_diameter: diameter of the bundle that rests in the cradle
    """
    # The measured bundle is 8.0 mm. Keep the fit and the structure derived from
    # the exposed diameter so nearby bundle sizes remain usable.
    length = 20.0
    clearance = 0.4
    back_thickness = 2.8
    floor_thickness = 2.4
    front_wall_thickness = 2.4
    front_wall_height = 0.65 * bundle_diameter

    inner_width = bundle_diameter + clearance
    front_inner_x = back_thickness + inner_width
    front_outer_x = front_inner_x + front_wall_thickness
    bundle_center_z = floor_thickness + 0.5 + bundle_diameter / 2.0

    # A small upright boss carries the single M4 hole. It rises above the
    # cradle so the screw head and driver never occupy the bundle's free space.
    screw_hole_diameter = 4.4
    screw_head_clearance_diameter = 8.4
    screw_head_clearance_radius = screw_head_clearance_diameter / 2.0
    screw_center_z = (
        bundle_center_z
        + bundle_diameter / 2.0
        + screw_head_clearance_radius
        + 0.6
    )
    back_base_height = 5.2
    boss_width = 10.0
    boss_y = (length - boss_width) / 2.0
    boss_bottom = back_base_height - 0.2
    boss_top = screw_center_z + screw_head_clearance_radius + 0.6

    back = Box(
        back_thickness,
        length,
        back_base_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        front_outer_x,
        length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    front_wall = Pos(front_inner_x, 0, floor_thickness - 0.2) * Box(
        front_wall_thickness,
        length,
        front_wall_height + 0.2,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    boss = Pos(0, boss_y, boss_bottom) * Box(
        back_thickness,
        boss_width,
        boss_top - boss_bottom,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = back + floor + front_wall + boss

    # The bore is normal to the wall-facing X face. Extend it past both ends
    # to guarantee a true through-hole after the boolean operation.
    screw_bore = Pos(-0.2, length / 2.0, screw_center_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole_diameter / 2.0,
        back_thickness + 0.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - screw_bore

    if draft:
        return body

    # Keep all functional cradle and mounting edges sharp: they define the fit
    # envelope. The geometry is already support-free and printable.
    return body
