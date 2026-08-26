from nurb import *

@part
def bundle_holder(bundle_diameter=8.0):
    """
    Wall-mounted cable bundle holder with M4 screw mounting.

    bundle_diameter: diameter of the cable bundle in mm
    """

    bundle_clearance = 0.4
    bundle_space = bundle_diameter + 2 * bundle_clearance

    screw_bore_dia = 4.4
    screw_head_dia = 8.4
    screw_seat_depth = 2.4

    part_length = 40.0
    mount_height = 10.0
    base_depth = 11.0

    back_thickness = 3.0
    groove_depth = bundle_diameter / 2 + 0.8
    lip_depth = 1.5  # Extend front wall

    # Create base body - solid rectangular block
    base = Box(base_depth, part_length, mount_height, align=(Align.MIN, Align.CENTER, Align.MIN))

    # Cut groove from top
    groove = Box(
        bundle_space + 0.5,
        part_length + 2,
        groove_depth,
        align=(Align.CENTER, Align.CENTER, Align.MAX)
    )

    # Screw bore through back plate
    screw_bore = Cylinder(
        radius=screw_bore_dia / 2,
        height=back_thickness + 1,
        align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )

    # Screw seat
    screw_seat = Cylinder(
        radius=screw_head_dia / 2,
        height=screw_seat_depth + 0.5,
        align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )

    # Cut from the back to remove space for the screw, but keep the back mounting face
    # This removes material from X=back_thickness onward, leaving the mounting plate
    back_cavity = Box(
        base_depth - back_thickness - 0.5,
        part_length + 2,
        mount_height - 2.0,
        align=(Align.MAX, Align.CENTER, Align.MAX)
    )

    # Assemble
    with BuildPart() as bp:
        add(base)

        # Position and cut groove
        groove_center_x = back_thickness + bundle_diameter / 2 + 1.0
        with Locations((groove_center_x, 0, mount_height)):
            add(groove, mode=Mode.SUBTRACT)

        # Subtract screw bore
        with Locations((0, 0, mount_height / 2)):
            add(screw_bore, mode=Mode.SUBTRACT)

        # Subtract screw seat
        with Locations((0, 0, mount_height / 2)):
            add(screw_seat, mode=Mode.SUBTRACT)

        # Subtract a cavity from the back to reduce material but preserve mounting face
        with Locations((base_depth, 0, mount_height)):
            add(back_cavity, mode=Mode.SUBTRACT)

    holder = bp.part
    holder = polish(holder, concave_edges(holder), 1.0)

    return holder
