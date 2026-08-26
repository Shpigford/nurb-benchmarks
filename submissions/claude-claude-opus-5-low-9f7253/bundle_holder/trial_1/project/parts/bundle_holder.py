from nurb import *


@part
def bundle_holder(
    bundle_diameter=8.0,
    bundle_clearance=0.6,
    back_thickness=4.0,
    floor_thickness=2.0,
    lip_thickness=2.6,
    lip_height_above_bundle=3.0,
    holder_length=10.5,
    screw_hole_width=4.4,
    draft=False,
):
    """A wall cradle that carries a horizontal cable bundle on one M4 screw.

    bundle_diameter: how thick the bundle of cables is
    bundle_clearance: extra slack around the bundle so it drops in
    back_thickness: how much material sits between the wall and the bundle
    floor_thickness: how thick the shelf the bundle rests on is
    lip_thickness: how thick the front lip that stops the bundle falling out is
    lip_height_above_bundle: how far the front lip rises past the bundle's middle
    holder_length: how much of the bundle's run the cradle grips, along the wall
    screw_hole_width: the clearance hole for the mounting screw (4.4 suits M4)
    """
    r = (bundle_diameter + bundle_clearance) / 2.0
    if r <= 0.5:
        reject("bundle_diameter is too small to cradle", "bundle_diameter")

    cx = back_thickness + r          # bundle axis, out from the wall
    cz = floor_thickness + r         # bundle axis, up from the bed
    width = cx + r + lip_thickness   # total reach away from the wall
    lip_top = cz + lip_height_above_bundle

    # The screw sits above the bundle, high enough that the head and a driver
    # sweep clear of the lip: 4.2 is the radius of that swept cylinder.
    screw_z = lip_top + 4.2 + 0.8
    back_height = screw_z + screw_hole_width / 2.0 + 2.5

    L = holder_length

    back = Box(back_thickness, L, back_height, align=(Align.MIN, Align.CENTER, Align.MIN))
    floor = Box(width, L, floor_thickness, align=(Align.MIN, Align.CENTER, Align.MIN))
    lip = Box(
        lip_thickness, L, lip_top,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    ).translate((cx + r, 0, 0))

    body = back + floor + lip

    bore = Cylinder(
        screw_hole_width / 2.0, back_thickness * 3,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).translate((back_thickness / 2.0, 0, screw_z))
    body = body - bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    wall = body.bounding_box().min.X
    concave = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e.bounding_box().min.X > wall + 1e-6
        and e not in concave
    )
    return polish(body, keep, 1.2)
