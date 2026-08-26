from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    holder_length=12.0,
    back_thickness=3.0,
    floor_thickness=2.0,
    front_thickness=2.0,
    clearance=0.4,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that holds a horizontal cable bundle under one M4 screw.

    bundle_diameter: how thick the cable bundle is across
    holder_length: how wide the holder is along the bundle
    back_thickness: how much material sits between the wall and the cradle
    floor_thickness: how thick the shelf under the bundle is
    front_thickness: how thick the lip that keeps the bundle on the wall is
    clearance: extra room around the bundle so it drops in by hand
    chamfer_size: how big the edge chamfers are
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be positive", param="bundle_diameter")

    open_width = bundle_diameter + clearance
    screw_hole = 4.4
    head_clear = 8.4 / 2 + 0.2

    depth = back_thickness + open_width + front_thickness
    front_height = floor_thickness + open_width * 0.7
    bundle_top = floor_thickness + open_width / 2 + bundle_diameter / 2
    screw_z = max(bundle_top, front_height) + head_clear + 0.6
    back_height = screw_z + screw_hole * 0.71 + 1.5

    def block(dx, dz, x=0.0):
        return Pos(x, 0, 0) * Box(
            dx, holder_length, dz, align=(Align.MIN, Align.CENTER, Align.MIN)
        )

    body = block(depth, floor_thickness)
    body += block(back_thickness, back_height)
    body += block(front_thickness, front_height, x=depth - front_thickness)

    axis = Pos(-1, 0, screw_z) * Rot(0, 90, 0)
    body -= axis * Cylinder(
        screw_hole / 2, back_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    # teardrop crest so the horizontal bore prints its own ceiling
    body -= axis * extrude(
        Triangle(a=screw_hole, B=45, C=45, align=(Align.CENTER, Align.MIN)),
        back_thickness + 2,
    )

    if draft:
        return body

    bb = body.bounding_box()

    def near_bore(e):
        # the screw bore is fit geometry: no lead-in chamfer at its mouth
        c = e.bounding_box().center()
        return (c.Y ** 2 + (c.Z - screw_z) ** 2) ** 0.5 < screw_hole

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.X > bb.min.X + 0.01
        and e.bounding_box().max.Z > bb.min.Z + 0.01
        and not near_bore(e)
    )
    keep = [e for e in keep if e not in concave_edges(body)]
    return polish(body, keep, chamfer_size)
