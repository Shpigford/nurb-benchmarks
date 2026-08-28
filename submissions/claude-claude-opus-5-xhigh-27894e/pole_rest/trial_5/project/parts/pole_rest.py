from math import cos, hypot, radians, sin

from nurb import *

# The bench interface, not a preference: several identical rests stand in a row and the
# pole lies across all of them, so the axis height is shared and never a slider.
AXIS_HEIGHT = 18.0

# Where the saddle's outer arc leaves the foot. Measured round from the bottom of the
# cradle, so 55 degrees puts the steepest outer overhang 35 degrees off vertical.
FLARE = 55.0


def _axis_gap(edge, axis_height):
    """How close an edge comes to the pole's axis, sampled along its length."""
    return min(
        hypot(p.X, p.Z - axis_height) for p in (edge @ t for t in (0.0, 0.25, 0.5, 0.75, 1.0))
    )


def _key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))


@part
def pole_rest(
    pole_diameter=float(measured("pole_diameter")),
    pole_clearance=0.25,
    cradle_wall=3.0,
    rest_length=24.0,
    chamfer_size=1.0,
    draft=False,
):
    """A saddle that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is across
    pole_clearance: the gap between the wet pole and the cradle it sits in
    cradle_wall: how much material sits behind the cradle surface
    rest_length: how far the rest spans along the pole
    chamfer_size: how big the chamfers on the exposed edges are
    """
    if pole_diameter < 4.0:
        reject(
            f"pole_diameter {pole_diameter} is too small to cradle: raise it above 4",
            param="pole_diameter",
        )
    if pole_clearance < 0.1:
        reject(
            f"pole_clearance {pole_clearance} binds on a wet finish: raise it to 0.1 or more",
            param="pole_clearance",
        )
    if cradle_wall < 2.0:
        reject(
            f"cradle_wall {cradle_wall} is under the 2mm minimum wall: raise it above 2",
            param="cradle_wall",
        )
    if rest_length < 20.0:
        reject(
            f"rest_length {rest_length} gives the pole too little bearing: raise it above 20",
            param="rest_length",
        )

    seat = pole_diameter / 2 + pole_clearance
    shell = seat + cradle_wall
    floor = AXIS_HEIGHT - seat
    if floor < 2.0:
        reject(
            f"pole_diameter {pole_diameter} leaves only {floor:.1f}mm of floor under the seat "
            f"at the fixed {AXIS_HEIGHT}mm axis height: lower it below "
            f"{2 * (AXIS_HEIGHT - 2.0 - pole_clearance):.0f}",
            param="pole_diameter",
        )

    # The foot meets the saddle where the outer arc is still climbing at 35 degrees off
    # vertical, so nothing on the outside ever overhangs past the 45 degree limit.
    foot_half = shell * sin(radians(FLARE))
    foot_top = AXIS_HEIGHT - shell * cos(radians(FLARE))

    # Outer shell: the lower half of a cylinder concentric with the pole. Everything from
    # the axis height up is cut away, which is what lets the pole drop straight in.
    body = Pos(0, 0, AXIS_HEIGHT) * (Rotation(90, 0, 0) * Cylinder(shell, rest_length))
    body -= Pos(0, 0, AXIS_HEIGHT + shell) * Box(4 * shell, rest_length + 4, 2 * shell)

    body += Pos(0, 0, foot_top / 2) * Box(2 * foot_half, rest_length, foot_top)
    body -= Pos(0, 0, AXIS_HEIGHT) * (Rotation(90, 0, 0) * Cylinder(seat, rest_length + 4))

    if shell > AXIS_HEIGHT:  # a fat pole drops the shell's arc under the bed
        body -= Pos(0, 0, -shell) * Box(4 * shell, rest_length + 4, 2 * shell)

    if draft:
        return body

    # Name what must stay sharp, then let `polish` chamfer whatever the kernel takes.
    # The cradle is the mating surface and never gets a lead-in; the bed face and the
    # concave junction where the arc lands on the foot are the doctrine's other two.
    bed = body.bounding_box().min.Z
    concave = {_key(e) for e in concave_edges(body)}
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > bed + 0.01
        and _key(e) not in concave
        and _axis_gap(e, AXIS_HEIGHT) > seat + 0.1
    )
    return polish(body, keep, chamfer_size)
