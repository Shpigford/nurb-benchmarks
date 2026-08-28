from nurb import *


@part
def bundle_holder(bundle_diameter: float = measured("bundle_diameter")):
    """A compact, print-flat cable-bundle clip with one recessed M4 mount.

    bundle_diameter: measured diameter of the cable bundle held by the clip
    """
    # The nominal cable gets a generous radial gap: a diameter 0.4 mm larger
    # than the bundle still has free passage through the full-length channel.
    clearance = 0.6
    back_thickness = 3.6
    shelf_height = 3.6
    front_wall_thickness = 1.6
    holder_length = 12.0

    screw_hole_diameter = 4.4
    screw_head_clearance_diameter = 8.8
    screw_head_seat_depth = 2.5

    bundle_radius = bundle_diameter / 2
    bundle_center_x = back_thickness + bundle_radius + clearance
    bundle_center_z = shelf_height + bundle_radius + clearance

    # The front wall is set just beyond the clearance envelope.  A one-mm move
    # away from the wall therefore meets it, while the open top remains easy to
    # load and the full Y length remains clear for threading a bundle through.
    front_wall_inner_x = bundle_center_x + bundle_radius + clearance
    front_wall_height = bundle_radius + 2.6
    holder_height = max(22.0, bundle_center_z + bundle_radius + 2.0)

    back = Box(
        back_thickness,
        holder_length,
        holder_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    shelf = Box(
        front_wall_inner_x + front_wall_thickness,
        holder_length,
        shelf_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    retaining_wall = Pos(front_wall_inner_x, 0, shelf_height) * Box(
        front_wall_thickness,
        holder_length,
        front_wall_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    # The counterbore opens toward +X.  Its 2.5 mm deep shank section leaves a
    # proper seat around the M4 bore; the larger cavity clears the pan head and
    # driver all the way out of the front of the back plate.
    screw_z = 16.0
    # Centering the horizontal cutters makes the X extents explicit: each one
    # deliberately runs past both faces before it is trimmed to its final span.
    shank_bore = Pos(back_thickness / 2, 0, screw_z) * Cylinder(
        screw_hole_diameter / 2,
        back_thickness + 0.1,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    full_head_cutter = Pos(back_thickness / 2, 0, screw_z) * Cylinder(
        screw_head_clearance_diameter / 2,
        back_thickness + 0.2,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    front_of_seat = Pos(screw_head_seat_depth, 0, screw_z) * Box(
        back_thickness - screw_head_seat_depth + 0.3,
        screw_head_clearance_diameter + 2.0,
        screw_head_clearance_diameter + 2.0,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    )
    head_recess = full_head_cutter & front_of_seat

    return (back + shelf + retaining_wall) - shank_bore - head_recess
