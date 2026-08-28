from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """Screw-down, open-top cable-bundle clip.

    bundle_diameter: measured diameter of the cable bundle held in the channel.
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    body_width = channel_width + 2 * wall_thickness
    overall_width = tab_length + body_width

    with BuildPart() as clip:
        # The bottom plate includes the mounting tab and the channel floor.
        Box(
            overall_width,
            part_length,
            base_thickness,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )

        # Add only the two square-cornered channel walls above the floor.
        with Locations((tab_length, 0, base_thickness)):
            Box(
                wall_thickness,
                part_length,
                channel_depth,
                align=(Align.MIN, Align.MIN, Align.MIN),
            )
        with Locations((tab_length + wall_thickness + channel_width, 0, base_thickness)):
            Box(
                wall_thickness,
                part_length,
                channel_depth,
                align=(Align.MIN, Align.MIN, Align.MIN),
            )

        # Vertical screw hole centered in the flat tab.
        with Locations((tab_length / 2, part_length / 2, 0)):
            Cylinder(
                screw_hole_diameter / 2,
                base_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    return clip.part
