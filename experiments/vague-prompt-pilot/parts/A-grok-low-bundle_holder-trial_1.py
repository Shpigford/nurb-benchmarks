from nurb import *


@part
def bundle_holder(
    holder_width=12.0,
    wall_plate=3.0,
    clip_wall=2.4,
    slide_gap=0.4,
    throat=6.8,
    draft=False,
):
    """Wall clip for a cable bundle. Screws to the wall with an M4 pan-head; cables drop in along the wall.

    holder_width: how far the clip spans along the bundle
    wall_plate: thickness of the back that sits on the wall
    clip_wall: thickness of the hook around the cables
    slide_gap: extra room around the measured bundle so it still slides
    throat: opening the cables squeeze through, next to the wall
    """
    bundle = measured("bundle_diameter")
    hole_dia = measured("m4_clearance")
    head_dia = measured("m4_pan_head_diameter")

    inner = bundle + slide_gap
    if throat >= bundle:
        reject(
            f"throat {throat} is as wide as the {bundle}mm bundle: the cables will drop out. Narrow it below {bundle}",
            param="throat",
        )
    if inner <= throat:
        reject(
            f"slide_gap leaves an inner channel of {inner}mm, not wider than throat {throat}: raise slide_gap",
            param="slide_gap",
        )
    if holder_width < head_dia + 2.0:
        reject(
            f"holder_width {holder_width} cannot seat an M4 pan head ({head_dia}mm): raise it above {head_dia + 2.0}",
            param="holder_width",
        )
    if clip_wall < 2.0:
        reject(
            f"clip_wall {clip_wall} is under 2mm: raise it to 2.0 or more",
            param="clip_wall",
        )
    if wall_plate < 2.5:
        reject(
            f"wall_plate {wall_plate} is too thin to bear an M4 pan head: raise it to 2.5 or more",
            param="wall_plate",
        )

    tip_x = wall_plate + throat
    inner_x = wall_plate + inner
    outer_x = inner_x + clip_wall
    floor_z = clip_wall
    inner_top_z = floor_z + inner
    hood_run = inner_x - tip_x
    tip_inner_z = inner_top_z + hood_run
    lip = 4.0
    lip_top = tip_inner_z + lip
    hole_z = lip_top + 6.0
    tab_top = hole_z + 6.0
    corner = 2.0

    with BuildPart() as built:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(
                    (0, 0),
                    (outer_x, 0),
                    (outer_x, inner_top_z),
                    (tip_x + clip_wall, inner_top_z + hood_run),
                    (tip_x + clip_wall, lip_top),
                    (tip_x, lip_top),
                    (tip_x, tip_inner_z),
                    (inner_x, inner_top_z),
                    (inner_x, floor_z + corner),
                    (inner_x - corner, floor_z),
                    (wall_plate + corner, floor_z),
                    (wall_plate, floor_z + corner),
                    (wall_plate, tab_top),
                    (0, tab_top),
                    close=True,
                )
            make_face()
        extrude(amount=holder_width / 2, both=True)

        hole_plane = Plane(
            origin=(wall_plate / 2, 0, hole_z),
            x_dir=(0, 1, 0),
            z_dir=(1, 0, 0),
        )
        with BuildSketch(hole_plane):
            Circle(hole_dia / 2)
        extrude(amount=wall_plate / 2 + 1.0, both=True, mode=Mode.SUBTRACT)

    body = built.part

    if draft:
        return body

    wall_x = body.bounding_box().min.X
    bed = body.bounding_box().min.Z
    concave = set(concave_edges(body))

    def polishable(e):
        if e in concave:
            return False
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        if bb.min.X <= wall_x + 0.05:
            return False
        if abs((bb.max.Y - bb.min.Y) - holder_width) > 0.2:
            return False
        return True

    keep = body.edges().filter_by(GeomType.LINE).filter_by(polishable)
    return polish(body, keep, 1.0)
