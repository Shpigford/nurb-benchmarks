from nurb import *


@part
def pole_rest(
    pole_width=measured("pole_diameter"),
    center_height=18.0,
    drop_in_room=0.5,
    side_thickness=3.0,
    rest_length=20.0,
    draft=False,
):
    """A bench rest that cradles a drying pole, one of a matching row.

    pole_width: how thick the pole is, measured across
    center_height: how high the pole's center sits above the bench
    drop_in_room: extra width in the cradle so the pole drops in and lifts out freely
    side_thickness: how much plastic is beside the cradle at its widest point
    rest_length: how long the rest runs along the pole
    """
    if drop_in_room < 0.3:
        reject(
            f"drop_in_room {drop_in_room} is under the 0.3mm a printed opening "
            "needs over what moves through it: raise it to 0.3 or more",
            param="drop_in_room",
        )
    cradle_radius = (pole_width + drop_in_room) / 2
    # The cradle's axis sits at the top face, so the mouth is the full pole
    # width plus room and the pole seats with its center at center_height.
    top = center_height + drop_in_room / 2
    floor = top - cradle_radius
    if floor < 2.0:
        reject(
            f"center_height {center_height} leaves only {floor:.1f}mm of plastic "
            "under the cradle: raise it until at least 2mm remains under the pole",
            param="center_height",
        )
    width = pole_width + drop_in_room + 2 * side_thickness

    body = Box(width, rest_length, top, align=(Align.CENTER, Align.CENTER, Align.MIN))
    groove = Pos(0, 0, top) * Rot(90, 0, 0) * Cylinder(cradle_radius, rest_length + 2)
    body = body - groove

    if draft:
        return body

    # Keep the polish off the bed-contact face and off the cradle: the groove
    # is the mating surface and gets no lead-in chamfer. Its rim lines and end
    # arcs all live inside |x| <= cradle_radius above the floor.
    def keep_edge(e):
        bb = e.bounding_box()
        if bb.max.Z < 1e-6:
            return False
        in_groove = (
            bb.max.X <= cradle_radius + 0.01
            and bb.min.X >= -cradle_radius - 0.01
            and bb.min.Z >= floor - 0.01
        )
        return not in_groove

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
