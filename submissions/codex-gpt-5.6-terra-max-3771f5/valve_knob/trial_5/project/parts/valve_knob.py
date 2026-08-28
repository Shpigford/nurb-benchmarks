from nurb import *


@part
def valve_knob(
    shaft_diameter: float = 8.0,
    shaft_across_flat: float = 6.5,
    bore_clearance: float = 0.8,
    knob_width: float = 29.0,
    knob_height: float = 16.0,
):
    """Square-grip replacement knob for an upright D-shaft.

    shaft_diameter: diameter across the rounded sides of the valve stem.
    shaft_across_flat: distance from the stem's flat to its opposite rounded side.
    bore_clearance: extra diameter and flat-to-round clearance for a printed fit.
    knob_width: width across the knob's narrow, flat-sided grip.
    knob_height: overall height as printed, from the bed to the bore opening.
    """
    # The stem is a circle clipped by its +X flat.  Applying the same clearance
    # to both measured spans keeps the bore parametrically tied to the shaft.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = -bore_radius + bore_across_flat

    bore_depth = knob_height - 3.0
    bore_center_z = knob_height / 2.0 - bore_depth / 2.0
    body = Box(knob_width, knob_width, knob_height)

    # Cut the round envelope first, then restore the material beyond the +X
    # flat.  The resulting vertical bore is a true D profile rather than a
    # round clearance hole, so it can transmit turning torque.
    round_bore = Cylinder(bore_radius, bore_depth).translate(
        (0.0, 0.0, bore_center_z)
    )
    flat_restore_width = knob_width / 2.0 - bore_flat_x
    flat_restore = Box(flat_restore_width, bore_diameter, bore_depth).translate(
        (bore_flat_x + flat_restore_width / 2.0, 0.0, bore_center_z)
    )
    return body.cut(round_bore).fuse(flat_restore)
