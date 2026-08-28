from math import cos, hypot, radians, sin

from nurb import *

# Every rest in the row carries the pole at the same height, so this is a fact
# about the bench rather than something a slider may move.
POLE_AXIS = measured("pole_axis_height")


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_clearance=0.25,
    cradle_wrap=150.0,
    cradle_wall=3.5,
    rest_length=24.0,
    foot_width=14.0,
    chamfer_size=1.2,
    draft=False,
):
    """One of a row of rests that hold a freshly finished pole while it dries.

    pole_diameter: how thick the pole is, measured across
    pole_clearance: the gap left all round the pole so it drops in without dragging on the finish
    cradle_wrap: how far the cradle curls around the pole, in degrees
    cradle_wall: how much material stands behind the cradle at its top edge
    rest_length: how much of the pole's length this one rest carries
    foot_width: how wide the rest stands on the bench
    chamfer_size: how much is taken off the exposed edges
    """
    seat_radius = pole_diameter / 2.0 + pole_clearance
    floor = POLE_AXIS - seat_radius
    if floor < 3.0:
        widest = 2.0 * (POLE_AXIS - 3.0 - pole_clearance)
        reject(
            f"a {pole_diameter:.1f}mm pole seated {POLE_AXIS:.1f}mm up leaves only "
            f"{floor:.1f}mm of floor under the cradle: keep the pole under "
            f"{widest:.1f}mm across",
            param="pole_diameter",
        )
    if not 120.0 <= cradle_wrap <= 180.0:
        reject(
            f"cradle_wrap {cradle_wrap:.0f} is outside 120 to 180 degrees: under 120 the "
            "pole balances instead of being cradled, and over 180 the seat closes over "
            "it so it cannot drop in from above",
            param="cradle_wrap",
        )

    half_arc = radians(cradle_wrap / 2.0)
    rim_x = seat_radius * sin(half_arc)
    rim_z = POLE_AXIS - seat_radius * cos(half_arc)
    half_width = rim_x + cradle_wall
    if foot_width < rim_z / 2.0:
        reject(
            f"foot_width {foot_width:.1f} under a rest {rim_z:.1f}mm tall tips the moment "
            f"the pole lands off centre: keep it above {rim_z / 2.0:.1f}",
            param="foot_width",
        )
    # The sides rise off the foot at 45 degrees, the one angle the whole part uses.
    shoulder_z = half_width - foot_width / 2.0
    if shoulder_z < 2.0:
        reject(
            f"foot_width {foot_width:.1f} leaves no flare under a {2 * half_width:.1f}mm "
            f"cradle: bring it under {2 * half_width - 4.0:.1f}",
            param="foot_width",
        )
    if shoulder_z > rim_z - 2.0 * chamfer_size:
        reject(
            f"foot_width {foot_width:.1f} is so narrow the 45 degree flare runs past the "
            f"top of the cradle: keep it above {2 * (half_width - rim_z) + 4.0:.1f}",
            param="foot_width",
        )

    outline = Polygon(
        (-foot_width / 2.0, 0.0),
        (foot_width / 2.0, 0.0),
        (half_width, shoulder_z),
        (half_width, rim_z),
        (-half_width, rim_z),
        (-half_width, shoulder_z),
        align=None,
    )
    seat = Pos(0.0, POLE_AXIS) * Circle(seat_radius)
    body = extrude(Plane.XZ * (outline - seat), amount=rest_length / 2.0, both=True)

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def on_seat(edge):
        # The seat is what the pole lies in: a lead-in chamfer at its mouth would
        # eat the wrap and print as a compound sliver.
        centre = edge.center()
        return hypot(centre.X, centre.Z - POLE_AXIS) < seat_radius + 0.5

    def on_shoulder(edge):
        # Where the 45 degree flare turns vertical. Chamfering an obtuse edge lays a
        # 22.5 degree facet, and every other facet on this part is at 45.
        centre = edge.center()
        return abs(centre.Z - shoulder_z) < 0.01 and abs(abs(centre.X) - half_width) < 0.01

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and not on_seat(e)
        and not on_shoulder(e)
    )
    return polish(body, keep, chamfer_size)
