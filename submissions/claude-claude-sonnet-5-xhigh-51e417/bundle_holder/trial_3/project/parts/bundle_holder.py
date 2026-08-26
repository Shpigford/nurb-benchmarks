from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    length=13.0,
    wall_thickness=2.0,
    draft=False,
):
    """
    bundle_diameter: diameter of the cable bundle the holder grips
    length: how far the holder runs along the cable bundle
    wall_thickness: thickness of material around the bundle tunnel and the screw pocket
    """
    if bundle_diameter <= 0:
        reject(f"bundle_diameter {bundle_diameter:g} must be positive", param="bundle_diameter")
    if wall_thickness <= 0:
        reject(f"wall_thickness {wall_thickness:g} must be positive", param="wall_thickness")

    # Bundle tunnel: enough slack to thread the bundle through, snug enough to hold it.
    tunnel_clearance = 0.45
    r_inner = (bundle_diameter + tunnel_clearance) / 2
    r_outer = r_inner + wall_thickness
    depth = 2 * r_outer  # wall to front, the post/dome's full reach

    # M4 pan-head screw, medium clearance column off the fastener table.
    shank_dia = 4.5
    shank_length = 2.6
    head_pocket_dia = 8.8
    r_pocket = head_pocket_dia / 2

    margin_below = 2.2  # bed to the screw pocket
    gap_wall = 1.8  # screw pocket to the bundle tunnel, solid separation
    edge_margin = 2.0  # screw pocket to each end of the part

    z_screw = margin_below + r_pocket
    z_tunnel = z_screw + r_pocket + gap_wall + r_inner

    min_length = 2 * (r_pocket + edge_margin)
    if length < min_length:
        reject(
            f"length {length:g} is under {min_length:.1f}, which is what the screw "
            f"pocket needs clear of both ends",
            param="length",
        )

    x_tunnel = r_outer
    y_screw = length / 2

    # Post: solid from the bed to the tunnel's centre, full front depth. Everything
    # below the tunnel's equator is filled in, so the tube above never overhangs.
    post = Box(depth, length, z_tunnel, align=(Align.MIN, Align.MIN, Align.MIN))

    # Tube: a full cylinder fused onto the post. Its lower half is already inside the
    # post's footprint, so the union only adds the dome riding above the equator.
    tube_outer = (
        Pos(x_tunnel, 0, z_tunnel)
        * Rotation(-90, 0, 0)
        * Cylinder(r_outer, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
    tunnel_hole = (
        Pos(x_tunnel, 0, z_tunnel)
        * Rotation(-90, 0, 0)
        * Cylinder(r_inner, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )

    # Screw bore: shank from the wall to the seat, then the head-and-driver pocket
    # the rest of the way to the front face.
    screw_shank = (
        Pos(0, y_screw, z_screw)
        * Rotation(0, 90, 0)
        * Cylinder(shank_dia / 2, shank_length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
    screw_pocket = (
        Pos(shank_length, y_screw, z_screw)
        * Rotation(0, 90, 0)
        * Cylinder(
            head_pocket_dia / 2,
            depth - shank_length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )

    body = post + tube_outer - tunnel_hole - screw_shank - screw_pocket

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    concave = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e not in concave
        and abs(e.bounding_box().max.Z - bed) > 1e-6
        and abs(e.bounding_box().max.X - back) > 1e-6
    )
    return polish(body, keep, 1.0)
