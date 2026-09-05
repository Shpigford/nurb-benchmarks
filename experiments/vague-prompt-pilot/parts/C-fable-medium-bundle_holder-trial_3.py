from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    channel_slack=1.0,
    holder_width=12.0,
    wall_thickness=2.4,
    floor_thickness=3.0,
    screw_hole_width=4.5,
    draft=False,
):
    """Wall clip for a cable bundle: drop the cables in along the wall, the lip keeps them put.

    bundle_diameter: how thick the cable bundle is
    channel_slack: extra channel width so the cables slide in and along easily
    holder_width: how wide the holder is along the wall
    wall_thickness: thickness of the back plate and the front lip
    floor_thickness: thickness of the floor under the bundle
    screw_hole_width: clearance hole for the wall screw (4.5 suits an M4)
    """
    if channel_slack < 0.2:
        reject(
            "channel_slack under 0.2 binds the bundle in the channel: "
            "raise it to 0.2 or more so the cables can slide",
            param="channel_slack",
        )
    if screw_hole_width < 2.0:
        reject(
            "screw_hole_width under 2mm prints as a smear: "
            "use 4.5 for an M4 clearance hole",
            param="screw_hole_width",
        )

    channel = bundle_diameter + channel_slack
    reach = wall_thickness + channel + wall_thickness
    lip_top = floor_thickness + bundle_diameter
    # Screw sits above the lip so a driver coming in along X clears it.
    screw_z = lip_top + screw_hole_width / 2.0 + 2.75
    # An M4 earns a fastener diameter of wall above its bore.
    back_height = screw_z + screw_hole_width / 2.0 + 4.0

    back = Pos((wall_thickness / 2, holder_width / 2, back_height / 2)) * Box(
        wall_thickness, holder_width, back_height
    )
    floor = Pos((reach / 2, holder_width / 2, floor_thickness / 2)) * Box(
        reach, holder_width, floor_thickness
    )
    lip = Pos((reach - wall_thickness / 2, holder_width / 2, lip_top / 2)) * Box(
        wall_thickness, holder_width, lip_top
    )
    body = back + floor + lip

    # 3mm structural relief at the two load-bearing channel-floor junctions,
    # cut before polish; it also cradles the round bundle.
    roots = ShapeList(concave_edges(body)).filter_by(Axis.Y)
    relieved = chamfer(roots, 3.0)
    hole = Pos((wall_thickness / 2, holder_width / 2, screw_z)) * Rot(0, 90, 0) * Cylinder(
        screw_hole_width / 2, wall_thickness + 1.0
    )
    body = relieved - hole

    if draft:
        return body

    # Keep the back face (against the wall), the bed face, the screw-hole rim
    # (the pan head bears there), and every concave edge sharp; polish lands
    # 1mm on the rest.
    concave = set(concave_edges(body))
    keep = (
        body.edges()
        .filter_by(GeomType.LINE)
        .filter_by(
            lambda e: e.bounding_box().max.X > 1e-6
            and e.bounding_box().max.Z > 1e-6
            and e not in concave
        )
    )
    return polish(body, keep, 1.0)
