from nurb import *

_M4_CLEAR = measured("m4_clearance")
_M4_HEAD = measured("m4_pan_head_diameter")


@part
def bundle_holder(
    clip_width=12.0,
    wall=2.4,
    opening=5.6,
    draft=False,
):
    """Wall clip that catches a sagging cable bundle.

    clip_width: how far the clip runs along the bundle
    wall: thickness of the trough, the wall-side lip, and the screw tab
    opening: gap above the wall-side lip where the cables slide in
    """
    bundle = measured("bundle_diameter")
    fit = measured("bundle_fit")
    bore = bundle + fit
    if opening >= bundle:
        reject(
            f"opening {opening} is as wide as the {bundle}mm bundle; the cables will fall out. Keep opening under {bundle}",
            param="opening",
        )
    if wall < 2.0:
        reject("wall under 2mm will print as a weak shell; raise wall to 2.0 or more", param="wall")

    r = bore / 2.0
    depth = wall + bore + wall
    cz = wall + r
    lip_h = cz + (bundle - opening) / 2.0
    trough_h = wall + bore + 1.0
    if lip_h >= trough_h - 1.0:
        reject(
            f"opening {opening} leaves no lip above the trough; shrink opening",
            param="opening",
        )

    tab_w = _M4_HEAD + 6.0
    tab_h = max(trough_h, _M4_HEAD + 8.0)
    plate = wall + 1.6

    body = Box(depth, clip_width, trough_h, align=(Align.MIN, Align.CENTER, Align.MIN))

    slot = Box(bore, clip_width + 4.0, trough_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    slot = slot.move(Pos(wall, 0, wall))
    trough = Cylinder(r, clip_width + 4.0).rotate(Axis.X, 90).move(Pos(wall + r, 0, cz))
    body = body - slot - trough

    mouth = Box(wall + r, clip_width + 4.0, trough_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    mouth = mouth.move(Pos(-0.1, 0, lip_h))
    body = body - mouth

    tab_y = clip_width / 2.0 + tab_w / 2.0
    tab = Box(plate, tab_w, tab_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    tab = tab.move(Pos(0, tab_y, 0))
    join = Box(plate, 2.0, min(trough_h, tab_h), align=(Align.MIN, Align.MIN, Align.MIN))
    join = join.move(Pos(0, clip_width / 2.0 - 0.5, 0))

    screw_z = tab_h / 2.0
    hole = Cylinder(_M4_CLEAR / 2.0, plate + 4.0).rotate(Axis.Y, 90).move(Pos(plate / 2.0, tab_y, screw_z))

    body = body + tab + join - hole

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05
        and e.bounding_box().min.Z > wall + 0.4
        and abs(e.bounding_box().center().Y - tab_y) > _M4_CLEAR
    )
    return polish(body, keep, 1.0)
