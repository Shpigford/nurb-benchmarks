from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    tunnel_clearance=0.6,
    wall_thickness=1.6,
    holder_length=12.4,
    draft=False,
):
    """
    bundle_diameter: how thick the cable bundle is, across
    tunnel_clearance: extra room the tunnel gives the bundle beyond its own diameter
    wall_thickness: how thick the material around the tunnel and the screw bore is
    holder_length: how far the holder runs along the cable bundle
    """
    tunnel_r = (bundle_diameter + tunnel_clearance) / 2.0
    tube_outer_r = tunnel_r + wall_thickness
    depth = 2.0 * tube_outer_r  # also the screw bore's total depth, back to front

    # M4 pan-head screw: shank clearance, seat depth before the head, head+driver clearance.
    shank_r = 4.6 / 2.0
    seat_depth = 2.8
    head_r = 8.8 / 2.0

    Zc_screw = wall_thickness + head_r
    # Zc_dome is the dome's own center, so the tunnel void's bottom (Zc_dome - tunnel_r) is what
    # actually has to clear the screw head hole's top (Zc_screw + head_r) by wall_thickness.
    Zc_dome = Zc_screw + head_r + wall_thickness + tunnel_r

    L = holder_length
    if L < 10.0:
        reject(f"holder_length {L} is under the 10mm minimum along the bundle", param="holder_length")
    min_length = 2.0 * head_r + 2.0 * wall_thickness
    if L < min_length:
        reject(
            f"holder_length {L} is under {min_length:.1f}, the minimum that leaves "
            f"wall_thickness {wall_thickness} of material beside the screw head",
            param="holder_length",
        )
    if seat_depth + 2.0 * wall_thickness > depth:
        reject(
            f"wall_thickness {wall_thickness} pinches the screw seat thinner than it needs to be; "
            "raise bundle_diameter/tunnel_clearance or lower wall_thickness",
            param="wall_thickness",
        )

    Yc = L / 2.0
    Xc = depth / 2.0  # dome and tunnel center X (== tube_outer_r)

    block = Box(depth, L, Zc_dome, align=(Align.MIN, Align.MIN, Align.MIN))
    dome = (
        Cylinder(tube_outer_r, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .rotate(Axis.X, -90)
        .translate((Xc, 0, Zc_dome))
    )
    body = block + dome

    tunnel_cut = (
        Cylinder(tunnel_r, L + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .rotate(Axis.X, -90)
        .translate((Xc, -1.0, Zc_dome))
    )
    shank_cut = (
        Cylinder(shank_r, seat_depth + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .rotate(Axis.Y, 90)
        .translate((-0.5, Yc, Zc_screw))
    )
    head_depth = depth - seat_depth + 1.0
    head_cut = (
        Cylinder(head_r, head_depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
        .rotate(Axis.Y, 90)
        .translate((seat_depth, Yc, Zc_screw))
    )

    body = body - tunnel_cut - shank_cut - head_cut

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > bed + 1e-6
        and e.bounding_box().max.X > back + 1e-6
        and e not in concave
    )
    return polish(body, keep, 1.0)
