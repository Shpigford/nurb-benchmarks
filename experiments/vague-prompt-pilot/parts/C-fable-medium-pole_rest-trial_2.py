from nurb import *


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_center_height=18.0,
    rest_length=20.0,
    wall_thickness=3.5,
    foot_flare=3.25,
    drop_in_clearance=0.5,
    chamfer_size=1.0,
    draft=False,
):
    """A drying rest that cradles a finished pole clear of the bench.

    pole_diameter: how thick the pole being finished is
    pole_center_height: how high the pole's center sits above the bench
    rest_length: how long the rest runs along the pole
    wall_thickness: how much material is beside the cradle at the top
    foot_flare: how much wider the base is than the body, each side
    drop_in_clearance: extra width in the cradle so the pole drops in freely
    chamfer_size: how big the edge chamfers are
    """
    cradle_radius = pole_diameter / 2 + drop_in_clearance / 2
    # The cradle arc's center sits half the clearance above the pole's
    # center, so the pole settles at exactly pole_center_height.
    cradle_center_z = pole_center_height + drop_in_clearance / 2
    height = cradle_center_z  # half-round cradle, open straight up

    floor = pole_center_height - pole_diameter / 2
    if floor < 2.0:
        reject(
            f"pole_center_height {pole_center_height} leaves only {floor:.1f}mm "
            f"of material under the pole: raise it above "
            f"{pole_diameter / 2 + 2.0:.1f}",
            param="pole_center_height",
        )
    if wall_thickness < 2.0:
        reject(
            f"wall_thickness {wall_thickness} is under the 2mm printable "
            f"minimum: raise it to 2 or more",
            param="wall_thickness",
        )

    top_width = 2 * cradle_radius + 2 * wall_thickness
    base_width = top_width + 2 * foot_flare

    pts = [
        (-base_width / 2, 0),
        (base_width / 2, 0),
        (top_width / 2, foot_flare),
        (top_width / 2, height),
        (-top_width / 2, height),
        (-top_width / 2, foot_flare),
    ]
    body = extrude(Plane.XZ * Polygon(*pts, align=None), amount=rest_length)

    # Center the block on Y so the pole axis runs through the origin
    # (extrude leaves it one-sided along Y).
    bb = body.bounding_box()
    body = Pos(0, -(bb.min.Y + bb.max.Y) / 2, 0) * body

    groove = Pos(0, 0, cradle_center_z) * Rot(90, 0, 0) * Cylinder(
        cradle_radius, rest_length + 2
    )
    body = body - groove

    if draft:
        return body
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6 and e not in concave
    )
    return polish(body, keep, chamfer_size)
