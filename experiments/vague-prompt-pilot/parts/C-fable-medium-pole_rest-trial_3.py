from nurb import *


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_center_height=18.0,
    drop_in_clearance=0.5,
    seat_length=15.0,
    wall_thickness=2.5,
    draft=False,
):
    """A bench rest that cradles a drying pole in a matching curved seat.

    pole_diameter: how wide the pole is, measured across
    pole_center_height: how high the pole's center sits above the bench
    drop_in_clearance: extra width in the seat so the pole drops in easily
    seat_length: how much of the pole the rest supports, along its length
    wall_thickness: how much plastic is left beside the seat at the rim
    """
    seat_radius = (pole_diameter + drop_in_clearance) / 2
    # The pole lies on the bottom of the seat, so the seat floor fixes the
    # center height no matter what the clearance is.
    seat_floor = pole_center_height - pole_diameter / 2
    if seat_floor < 3.0:
        reject(
            f"pole_center_height {pole_center_height} leaves only {seat_floor:.1f}mm "
            f"of plastic under a {pole_diameter}mm pole: raise it above "
            f"{pole_diameter / 2 + 3.0:.1f}",
            param="pole_center_height",
        )
    seat_center = seat_floor + seat_radius
    # Semicircular seat: the block's top rim sits level with the seat's center,
    # so the mouth is the seat's full width and the pole drops straight in.
    top = seat_center
    half_width = seat_radius + wall_thickness

    body = Pos(0, 0, top / 2) * Box(2 * half_width, seat_length, top)
    seat = Pos(0, 0, seat_center) * Rot(90, 0, 0) * Cylinder(
        seat_radius, seat_length + 2
    )
    body -= seat

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def polishable(e):
        bb = e.bounding_box()
        if bb.max.Z <= bed + 1e-6:
            return False  # lies in the bed face
        # The seat is the mating surface: leave its rim and end arcs untouched.
        if abs(bb.min.X) <= seat_radius + 0.05 and abs(bb.max.X) <= seat_radius + 0.05:
            if bb.min.Z >= seat_floor - 0.05:
                return False
        return True

    keep = body.edges().filter_by(polishable)
    return polish(body, keep, 1.0)
