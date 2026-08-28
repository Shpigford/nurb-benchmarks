from nurb import *


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_center_height=18.0,
    pole_clearance=0.25,
    cradle_wall=3.0,
    rest_length=22.0,
    foot_flare=3.0,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is across the finished stock
    pole_center_height: how high above the bench the pole's centre line sits
    pole_clearance: the air gap held between the seat and the wet finish
    cradle_wall: how much material stands behind the seat at its widest
    rest_length: how far the rest runs along the pole
    foot_flare: how far the base spreads out past the body, for footing
    """
    seat_radius = pole_diameter / 2.0 + pole_clearance
    floor = pole_center_height - seat_radius
    if floor < 3.0:
        widest = 2.0 * (pole_center_height - 3.0 - pole_clearance)
        reject(
            f"a {pole_diameter:.1f}mm pole seated at {pole_center_height:.1f} leaves "
            f"{floor:.1f}mm of floor under the seat: keep pole_diameter under "
            f"{widest:.1f}, or raise pole_center_height",
            param="pole_diameter",
        )

    body_half = seat_radius + cradle_wall
    base_half = body_half + foot_flare

    # One extruded profile: a plinth flaring out at 45 degrees to a broad foot,
    # then straight walls up to the rim, which sits level with the pole's axis.
    profile = Plane.XZ * Polygon(
        (base_half, 0.0),
        (body_half, foot_flare),
        (body_half, pole_center_height),
        (-body_half, pole_center_height),
        (-body_half, foot_flare),
        (-base_half, 0.0),
        align=None,
    )
    blank = extrude(profile, amount=rest_length / 2.0, both=True)

    # The seat is a half round: the rim lands on the axis, so the pole lowers
    # straight down into it and is wrapped through a full 180 degrees.
    seat = (
        Pos(0, 0, pole_center_height)
        * Rot(90, 0, 0)
        * Cylinder(seat_radius, rest_length + 2.0)
    )
    body = blank - seat
    if draft:
        return body

    # Name what must stay sharp, then let `polish` chamfer whatever the kernel takes.
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)

    def on_seat(edge):
        for v in edge.vertices():
            radial = (v.X**2 + (v.Z - pole_center_height) ** 2) ** 0.5
            if abs(radial - seat_radius) > 0.01:
                return False
        return True

    keep = [
        e
        for e in body.edges()
        if e.bounding_box().min.Z > bed + 1e-6
        and not on_seat(e)
        and not any(c.is_same(e) for c in concave)
    ]
    # 1.2 rather than 1.0: three chamfers meeting at a top corner leave a
    # 0.866 * size**2 triangle, and at 1.0 that facet lands under the 1mm2 floor.
    return polish(body, keep, 1.2)
