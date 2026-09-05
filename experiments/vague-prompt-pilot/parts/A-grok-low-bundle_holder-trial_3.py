from math import sqrt

from nurb import *


@part
def bundle_holder(
    clip_length=10.0,
    wall=2.5,
    opening=6.0,
    plate_thickness=4.0,
    draft=False,
):
    """Wall clip that tucks an 8mm cable bundle against the wall on one M4 pan-head screw.

    clip_length: how far the clip runs along the cables
    wall: thickness of the hook, floor, and lip
    opening: gap the bundle squeezes through at the top, along the wall
    plate_thickness: how thick the back plate is, screw goes through this
    """
    bundle = measured("bundle_diameter")
    hole_dia = measured("m4_clearance")
    head_dia = measured("m4_pan_head_diameter")

    if wall < 2.0:
        reject("wall 2mm is the print minimum: raise wall above 2", param="wall")
    if opening >= bundle:
        reject(
            f"opening {opening} is as wide as the {bundle}mm bundle so it will drop out: lower opening",
            param="opening",
        )
    if opening < bundle * 0.5:
        reject(
            f"opening {opening} is too tight for the {bundle}mm bundle to squeeze in",
            param="opening",
        )
    if clip_length < 6.0:
        reject("clip_length under 6mm is too short to hold the bundle", param="clip_length")
    if plate_thickness < 3.0:
        reject(
            "plate_thickness under 3mm is too thin for an M4 against the wall",
            param="plate_thickness",
        )

    inner_r = bundle / 2 + 0.2
    inner_w = 2 * inner_r
    lip_run = (inner_w - opening) / 2
    if lip_run < 1.2:
        reject(
            f"opening {opening} leaves a lip under 1.2mm; narrow the opening",
            param="opening",
        )

    back = max(wall, plate_thickness)
    ox = back + inner_w + wall
    floor_chamfer = 1.5
    blunt = 1.2
    # Floor, then bundle height, then 45° lip, then a blunt tip so 1mm polish cannot knife it.
    trough_top = wall + inner_w
    hook_h = trough_top + lip_run + blunt

    # CCW outer profile in XZ: wall at x=0, bed at z=0, mouth at +Z.
    outer = [
        (0, 0),
        (ox, 0),
        (ox, hook_h),
        (ox - wall - lip_run, hook_h),
        (ox - wall - lip_run, hook_h - blunt),
        (ox - wall, trough_top),
        (ox - wall, wall + floor_chamfer),
        (ox - wall - floor_chamfer, wall),
        (back + floor_chamfer, wall),
        (back, wall + floor_chamfer),
        (back, trough_top),
        (back + lip_run, hook_h - blunt),
        (back + lip_run, hook_h),
        (0, hook_h),
    ]
    with BuildSketch(Plane.XZ) as hook_sk:
        Polygon(*outer)
    hook = extrude(hook_sk.sketch, clip_length)
    hook = hook.move(
        Location(
            (
                -hook.bounding_box().min.X,
                -hook.bounding_box().min.Y,
                -hook.bounding_box().min.Z,
            )
        )
    )

    tab_w = max(head_dia + 4.0, hole_dia + 6.0)
    tab_h = max(hook_h, head_dia + 6.0)
    overlap = 3.0
    tab = Box(back, tab_w + overlap, tab_h, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = tab.move(Location((0, clip_length - overlap, 0)))

    hole_y = clip_length - overlap + (tab_w + overlap) / 2
    hole_z = tab_h / 2
    with BuildSketch(Plane.YZ.offset(back / 2)) as hole_sk:
        with Locations((hole_y, hole_z)):
            Circle(hole_dia / 2)
            Polygon(
                (-hole_dia / (2 * sqrt(2)), hole_dia / (2 * sqrt(2))),
                (0, hole_dia / sqrt(2)),
                (hole_dia / (2 * sqrt(2)), hole_dia / (2 * sqrt(2))),
            )
    screw = extrude(hole_sk.sketch, back + 4, both=True)

    body = hook + tab - screw
    bb = body.bounding_box()
    body = body.move(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))

    if draft:
        return body
    bed = body.bounding_box().min.Z
    sharp = concave_edges(body)
    bed_edges = body.edges().filter_by(lambda e: e.bounding_box().min.Z <= bed + 0.05)
    keep = body.edges() - sharp - bed_edges
    return polish(body, keep, 1.0)
