from math import cos, radians, sin

from nurb import *

# The row of rests is the interface: every one of them carries the pole's axis at
# this height, along Y, over the middle of its own footprint. It is not a parameter
# because a rest that disagrees with its neighbours is not a rest.
AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=float(measured("pole_diameter")),
    cradle_gap=0.25,
    cradle_wrap=150.0,
    wall_thickness=3.0,
    foot_width=18.0,
    rest_length=30.0,
    rim_height=4.5,
    chamfer_size=1.2,
    draft=False,
):
    """A cradle that holds a freshly finished pole off the bench while it dries.

    pole_diameter: how thick the pole is across
    cradle_gap: how much wider than the pole the cradle is cut, so wet finish never drags
    cradle_wrap: how far around the pole the cradle reaches, in degrees
    wall_thickness: how much material stands behind the cradle at its top rim
    foot_width: how wide the foot is where it stands on the bench
    rest_length: how far the rest runs along the pole
    rim_height: the straight face under the top edge of each arm
    chamfer_size: how much is taken off the exposed edges
    """
    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + cradle_gap
    half_wrap = radians(cradle_wrap / 2.0)

    rim_z = AXIS_HEIGHT - cradle_radius * cos(half_wrap)  # top of the arms
    rim_x = cradle_radius * sin(half_wrap)                # cradle half-width there
    shoulder_half = rim_x + wall_thickness                # outer half-width there
    foot_half = foot_width / 2.0
    flare_rise = shoulder_half - foot_half                # 45 degrees, so rise == run
    shoulder_z = rim_z - rim_height
    foot_z = shoulder_z - flare_rise
    floor = AXIS_HEIGHT - cradle_radius                   # material under the cradle

    if cradle_gap < 0.1:
        reject(
            f"cradle_gap {cradle_gap} binds on the pole: below 0.1 the fit varies by "
            "machine and the finish drags. Raise it to 0.1 or more.",
            param="cradle_gap",
        )
    if cradle_wrap < 120.0:
        reject(
            f"cradle_wrap {cradle_wrap} degrees balances the pole on two edges instead "
            "of cradling it: raise it to 120 or more.",
            param="cradle_wrap",
        )
    if cradle_wrap > 180.0:
        reject(
            f"cradle_wrap {cradle_wrap} degrees closes the cradle over the pole, so it "
            "can no longer be lowered straight in: lower it to 180 or less.",
            param="cradle_wrap",
        )
    if floor < 3.0:
        reject(
            f"pole_diameter {pole_diameter} puts the bottom of the cradle {floor:.1f} "
            f"above the bench, too thin a floor to print: this rest holds poles up to "
            f"{2 * (AXIS_HEIGHT - 3.0 - cradle_gap):.0f} across.",
            param="pole_diameter",
        )
    if flare_rise < 1.0:
        reject(
            f"foot_width {foot_width} is as wide as the arms, so there is nothing for "
            f"the 45 degree flare to do: lower it below {2 * shoulder_half - 2.0:.1f}.",
            param="foot_width",
        )
    if foot_z < 3.0:
        reject(
            f"foot_width {foot_width} leaves only {foot_z:.1f} of upright foot under "
            f"the flare: raise it above {foot_width + 2 * (3.0 - foot_z):.1f}.",
            param="foot_width",
        )

    # One profile in XZ, extruded along the pole. Upright foot, a 45 degree flare out
    # to the arms, then a straight rim face: the same facet angle the chamfers use.
    outline = [
        (-foot_half, 0.0),
        (foot_half, 0.0),
        (foot_half, foot_z),
        (shoulder_half, shoulder_z),
        (shoulder_half, rim_z),
        (-shoulder_half, rim_z),
        (-shoulder_half, shoulder_z),
        (-foot_half, foot_z),
    ]
    blank = extrude(
        Plane.XZ * make_face(Polyline(*outline, close=True)),
        amount=rest_length / 2.0,
        both=True,
    )

    # The cradle itself: the pole's own circle, opened by the gap, lying along Y. It
    # stops short of the pole's equator, so the pole drops straight in from above.
    cradle = (
        Pos(0, 0, AXIS_HEIGHT)
        * Rot(90, 0, 0)
        * Cylinder(radius=cradle_radius, height=rest_length + 4.0)
    )
    body = blank - cradle

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def key(edge):
        c = edge.center()
        return (round(c.X, 3), round(c.Y, 3), round(c.Z, 3))

    concave = {key(e) for e in concave_edges(body)}

    keep = []
    for edge in body.edges():
        if edge.bounding_box().max.Z - bed < 1e-6:
            continue  # lies in the bed face
        if key(edge) in concave:
            continue  # the flare's toe, where a chamfer is a feather edge
        c = edge.center()
        if (c.X**2 + (c.Z - AXIS_HEIGHT) ** 2) ** 0.5 <= cradle_radius + 0.05:
            continue  # bounds the cradle, which is what the pole lies on
        keep.append(edge)

    return polish(body, keep, chamfer_size)
