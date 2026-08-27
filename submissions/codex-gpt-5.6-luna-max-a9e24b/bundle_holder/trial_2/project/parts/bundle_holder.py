from nurb import *


# Load the recorded workshop measurement so the source documents where the
# default came from.  The function parameter remains the driving value so the
# holder can be resized from the viewer or by a caller.
_recorded_bundle_diameter = measured("bundle_diameter")


@part
def bundle_holder(bundle_diameter=8.0, draft=False):
    """Wall-mounted cable-bundle holder.

    bundle_diameter: diameter of the bundle that passes along Y
    """
    d = float(bundle_diameter)
    if d <= 0.0:
        reject("bundle_diameter must be greater than 0mm", param="bundle_diameter")

    # The holder is a grounded, open channel.  The extra 0.4mm on each side
    # leaves a generous 0.8mm diametral running clearance around the bundle.
    length = 12.0
    back_thickness = 3.0
    floor_thickness = 2.4
    front_wall_thickness = 2.0
    running_clearance_each_side = 0.4
    bundle_bottom_clearance = 0.4

    front_inner_x = back_thickness + d + 2.0 * running_clearance_each_side
    front_outer_x = front_inner_x + front_wall_thickness
    bundle_center_x = back_thickness + running_clearance_each_side + d / 2.0
    bundle_center_z = floor_thickness + bundle_bottom_clearance + d / 2.0

    # The rail is tall enough to intercept a 1mm +X move.  Keep the screw
    # head/driver cylinder 0.4mm above its top so the fastener remains clear.
    front_wall_height = floor_thickness + d + 1.0
    screw_head_driver_radius = 8.4 / 2.0
    screw_center_z = front_wall_height + screw_head_driver_radius + 0.4
    back_height = screw_center_z + 4.3
    screw_center_y = length / 2.0

    floor = Box(
        front_outer_x,
        length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    back = Box(
        back_thickness,
        length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    front_wall = Pos(front_inner_x, 0, 0) * Box(
        front_wall_thickness,
        length,
        front_wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # M4 medium clearance bore, axis along +X, opening on the back face.
    # It passes through the full 3mm back plate and stops in the open space;
    # the front face of that plate is the pan-head seat.
    screw_bore = Pos(-0.1, screw_center_y, screw_center_z) * Cylinder(
        2.2,
        back_thickness + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
        rotation=(0, 90, 0),
    )

    body = (back + floor + front_wall) - screw_bore
    if draft:
        return body

    return body
