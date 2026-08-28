from nurb import *


@part
def pole_rest(
    pole_diameter=20.0,
    rest_length=30.0,
    side_wall=2.0,
    draft=False,
):
    """An open-top drying saddle for a freshly finished pole.

    pole_diameter: outside diameter of the pole the circular saddle supports.
    rest_length: length of the saddle along the pole.
    side_wall: radial material behind the soft-finish contact surface.
    """
    axis_height = 18.0
    clearance = 0.15

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")
    if side_wall < 2.0:
        reject(
            "side_wall must be at least 2.0mm for a printable cradle wall",
            param="side_wall",
        )
    if rest_length < 20.0:
        reject(
            "rest_length must be at least 20mm so the pole is supported along its length",
            param="rest_length",
        )

    seat_radius = pole_diameter / 2.0 + clearance
    if seat_radius >= axis_height:
        reject(
            "pole_diameter is too large for an 18mm-high pole axis",
            param="pole_diameter",
        )

    # The box ends 2mm below the pole axis. Its circular cutout therefore leaves
    # a 157-degree lower arc at the nominal size: more than the required 120
    # degrees, while keeping every bit of the saddle below the descending pole.
    saddle_top = axis_height - 2.0
    outside_width = 2.0 * (seat_radius + side_wall)
    blank = Box(
        outside_width,
        rest_length,
        saddle_top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Make the bore longer than the rest so its ends stay completely open. The
    # pole runs along Y; rotating the cylinder puts its axis on Y at Z = 18.
    bore = Cylinder(
        seat_radius,
        rest_length + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).rotate(Axis.X, 90.0)
    bore = bore.translate((0.0, 0.0, axis_height))
    return blank - bore
