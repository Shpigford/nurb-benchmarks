from math import sqrt

from nurb import *


@part
def bundle_holder(draft=False):
    """Wall clip for a cable bundle. Screws on with one M4 pan-head; the bundle
    slides down the wall into a lipped cradle.

    bundle_diameter: measured taped-bundle diameter (from measurements.toml)
    wall_thickness: back plate and front-wall thickness
    width: extrusion along the bundle (Y)
    foot_depth: how far the mounting foot sticks out from the wall
    foot_height: height of the screw-head seat
    screw_hole: M4 clearance through the foot
    screw_height: screw axis height from the bed
    """
    D = measured("bundle_diameter")

    wall_thickness = 3.0
    width = 10.0
    foot_depth = 6.0
    foot_height = 12.0
    screw_hole = 4.5
    screw_height = 6.0
    overshoot = 2.0

    r = (D + 1.0) / 2.0
    xc = wall_thickness + r
    gap = 0.75 * D
    slot_back = wall_thickness
    slot_front = wall_thickness + gap
    # Keep the saddle at least r+2.5 off the 45° underside (Z = X + 6).
    zc_min = xc + 6.0 + (r + 2.5) * sqrt(2.0)
    zc = max(24.0, zc_min)
    lip_outer_x = xc + r
    lip_tip_z = zc + (lip_outer_x - slot_front)
    part_top = lip_tip_z + 3.0
    front_x = lip_outer_x + wall_thickness
    chamfer_z = foot_height + (front_x - foot_depth)
    ramp_top = part_top + wall_thickness

    xz_body = Plane.XZ
    xz_cut = Plane.XZ.offset(overshoot)
    cut_span = width + 2.0 * overshoot

    with BuildPart() as bp:
        with BuildSketch(xz_body):
            Polygon(
                (0, 0),
                (foot_depth, 0),
                (foot_depth, foot_height),
                (front_x, chamfer_z),
                (front_x, part_top),
                (wall_thickness, part_top),
                (0, ramp_top),
            )
        extrude(amount=-width)

        # Cut A — channel saddle (lower half-disc).
        with BuildSketch(xz_cut):
            with Locations((xc, zc)):
                Circle(r)
                Rectangle(
                    2.0 * r + 2.0,
                    r + 2.0,
                    align=(Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
        extrude(amount=-cut_span, mode=Mode.SUBTRACT)

        # Cut B — entry slot (plate front to lip inner face).
        with BuildSketch(xz_cut):
            Polygon(
                (slot_back, zc),
                (slot_front, zc),
                (slot_front, ramp_top + overshoot),
                (slot_back, ramp_top + overshoot),
            )
        extrude(amount=-cut_span, mode=Mode.SUBTRACT)

        # Cut C — lip underside 45° (prints without support).
        with BuildSketch(xz_cut):
            Polygon(
                (slot_front, zc),
                (lip_outer_x, zc),
                (slot_front, lip_tip_z),
            )
        extrude(amount=-cut_span, mode=Mode.SUBTRACT)

        # Cut D — mouth lead-in.
        with BuildSketch(xz_cut):
            Polygon(
                (slot_front, part_top),
                (slot_front, part_top - 2.0),
                (slot_front + 2.0, part_top),
            )
        extrude(amount=-cut_span, mode=Mode.SUBTRACT)

        # Cut E — M4 clearance through the foot.
        with Locations((foot_depth / 2.0, width / 2.0, screw_height)):
            Cylinder(
                screw_hole / 2.0,
                foot_depth + 2.0 * overshoot,
                rotation=(0, 90, 0),
                mode=Mode.SUBTRACT,
            )

    body = bp.part
    # Spec: no fillets; the four modelled 45° faces are the only chamfers.
    _ = draft
    return body
