from nurb import *


@part
def bundle_holder(
    bundle_diameter=float(measured("bundle_diameter")),
    draft=False,
):
    """Wall clip that holds a cable bundle with one M4 pan-head screw.

    bundle_diameter: width of the taped cable bundle the clip holds
    """
    if bundle_diameter < 4.0:
        reject(
            "bundle_diameter 4mm is the smallest this clip can hold: raise it",
            param="bundle_diameter",
        )

    # 0.4 total clearance so an 8.0 bundle sits in an 8.4 pocket.
    inner = bundle_diameter + 0.4
    wall = 2.4
    back = 3.0
    length = 12.0
    pad_height = 14.0
    hole = 4.4

    floor = wall
    channel_top = floor + inner
    total_z = channel_top + pad_height
    hole_z = channel_top + pad_height / 2.0

    plate = Box(back, length, total_z, align=(Align.MIN, Align.CENTER, Align.MIN))
    channel_floor = Box(
        inner, length, wall, align=(Align.MIN, Align.CENTER, Align.MIN)
    ).moved(Location((back, 0, 0)))
    front = Box(
        wall, length, channel_top, align=(Align.MIN, Align.CENTER, Align.MIN)
    ).moved(Location((back + inner, 0, 0)))
    body = plate + channel_floor + front

    bore = Cylinder(hole / 2.0, back + 4.0, rotation=(0, 90, 0)).moved(
        Location((back / 2.0, 0, hole_z))
    )
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    sharp = concave_edges(body)
    keep = [
        e
        for e in body.edges()
        if e.bounding_box().min.Z > bed + 0.05
        and e.geom_type != GeomType.CIRCLE
        and e not in sharp
        and e.bounding_box().size.Y > 8.0
        # Keep the inner lip of the channel square so a 1mm chamfer
        # cannot thin the +X catch below the 0.8mm blocking floor.
        and (
            0.5 * (e.bounding_box().min.X + e.bounding_box().max.X) < back + 0.2
            or 0.5 * (e.bounding_box().min.X + e.bounding_box().max.X)
            > back + inner + 0.2
        )
    ]
    return polish(body, keep, 1.0)
