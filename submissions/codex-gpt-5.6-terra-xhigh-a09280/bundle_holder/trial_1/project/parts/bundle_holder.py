from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    holder_length=12.0,
    fit_clearance=0.4,
    draft=False,
):
    """A one-screw, open-top wall holder for a horizontal cable bundle.

    bundle_diameter: measured width of the cable bundle.
    holder_length: length of uninterrupted cable support along the wall.
    fit_clearance: extra width around the bundle's measured diameter.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")
    if holder_length < 10.0:
        reject("holder_length must be at least 10 mm for continuous cable support", param="holder_length")
    if fit_clearance < 0.4:
        reject("fit_clearance must be at least 0.4 mm so the bundle can fit", param="fit_clearance")

    # The cavity is deliberately 0.4 mm wider than the measured bundle. The back
    # plate stops inward motion, the grounded floor stops downward motion, and the
    # front rail stops outward motion while leaving the top open for installation.
    plate_thickness = 3.0
    floor_thickness = 3.0
    front_rail_thickness = 2.4
    bundle_space = bundle_diameter + fit_clearance
    cavity_width = bundle_space
    cable_center_z = floor_thickness + bundle_space / 2.0

    # Keep the M4 head completely above the cable's free envelope. The plate is
    # tall enough to leave 2 mm of material around the 8.4 mm head clearance zone.
    m4_head_radius = 4.2
    screw_center_z = floor_thickness + bundle_space + m4_head_radius + 0.6
    plate_height = screw_center_z + m4_head_radius + 2.0
    rail_height = cable_center_z + 1.5
    total_depth = plate_thickness + cavity_width + front_rail_thickness

    plate = Box(
        plate_thickness,
        holder_length,
        plate_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        total_depth,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    front_rail = Box(
        front_rail_thickness,
        holder_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((plate_thickness + cavity_width, 0.0, 0.0))
    body = plate + floor + front_rail

    # M4 medium-clearance through bore. Its 3 mm wall thickness before the head
    # seat exceeds the required 2.4 mm, and the 8.4 mm pan-head envelope leaves the
    # part immediately from the plate's front face without entering the cable space.
    m4_bore_radius = 2.2
    bore = Cylinder(
        m4_bore_radius,
        plate_thickness + 0.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, 90.0).translate(
        (-0.05, holder_length / 2.0, screw_center_z - m4_bore_radius)
    )
    return body - bore
