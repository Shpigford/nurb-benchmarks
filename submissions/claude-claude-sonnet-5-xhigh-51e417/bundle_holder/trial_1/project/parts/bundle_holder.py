from nurb import *


@part
def bundle_holder(
    bundle_diameter=8.0,
    length=16.0,
    channel_wall=1.2,
    draft=False,
):
    """
    bundle_diameter: the cable bundle's diameter across
    length: how far the holder runs along the bundle
    channel_wall: material thickness around the cable channel and the screw boss
    """
    if length < 10.0:
        reject(f"length {length} is under the 10mm minimum run along the bundle: raise it above 10.0", param="length")
    if channel_wall < 0.8:
        reject(f"channel_wall {channel_wall} is under the 0.8mm the retaining material needs to hold anything: raise it above 0.8", param="channel_wall")

    r_bundle = bundle_diameter / 2
    channel_radius = r_bundle + 0.21          # channel across = bundle_diameter + 0.42, clears the 8.4 test
    tube_outer_radius = channel_radius + channel_wall
    tube_size = 2 * tube_outer_radius         # square housing around the channel, channel_wall on every side

    shank_radius = 2.2                        # 4.4 through-bore for the M4 shank, per the mount spec
    seat_depth = 3.0                          # >= 2.4mm of material before the screw head seats
    head_clear_radius = 4.35                  # clears the tested 8.4 head-and-driver envelope
    counterbore_depth = 2.0
    boss_depth = seat_depth + counterbore_depth
    screw_boss_radius = head_clear_radius + channel_wall
    boss_size = 2 * screw_boss_radius

    y_screw = length / 2
    boss_width = min(length, boss_size + 2.0)
    z_screw = tube_size + screw_boss_radius   # stacked flush on the housing's flat top

    housing = Box(tube_size, length, tube_size, align=(Align.MIN, Align.MIN, Align.MIN))

    plane_channel = Plane(origin=(tube_outer_radius, -0.5, tube_outer_radius), z_dir=(0, 1, 0))
    channel_cut = extrude(plane_channel * Circle(channel_radius), amount=length + 1.0)

    screw_boss = Pos(0, y_screw - boss_width / 2, tube_size) * Box(
        boss_depth, boss_width, boss_size, align=(Align.MIN, Align.MIN, Align.MIN),
    )

    plane_shank = Plane(origin=(-0.5, y_screw, z_screw), z_dir=(1, 0, 0))
    shank_cut = extrude(plane_shank * Circle(shank_radius), amount=seat_depth + 0.5)

    plane_head = Plane(origin=(seat_depth - 0.1, y_screw, z_screw), z_dir=(1, 0, 0))
    head_cut = extrude(plane_head * Circle(head_clear_radius), amount=boss_depth - seat_depth + 0.6)

    body = housing + screw_boss
    body -= channel_cut
    body -= shank_cut
    body -= head_cut

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    front_end = body.bounding_box().max.Y

    def on_bed_or_back(e):
        bb = e.bounding_box()
        return (abs(bb.min.Z - bed) < 1e-6 and abs(bb.max.Z - bed) < 1e-6) or (
            abs(bb.min.X - back) < 1e-6 and abs(bb.max.X - back) < 1e-6
        )

    def is_channel_rim(e):
        bb = e.bounding_box()
        span = 2 * channel_radius
        return (
            abs(bb.min.Y - bb.max.Y) < 1e-6
            and abs((bb.max.X - bb.min.X) - span) < 1e-3
            and abs((bb.max.Z - bb.min.Z) - span) < 1e-3
        )

    def on_end_cap(e):
        bb = e.bounding_box()
        if abs(bb.min.Y - bb.max.Y) > 1e-6:
            return False
        return abs(bb.min.Y - 0.0) < 1e-6 or abs(bb.min.Y - front_end) < 1e-6

    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: not on_bed_or_back(e) and not is_channel_rim(e) and not on_end_cap(e)
    ).filter_by(lambda e: e not in concave)
    return polish(body, keep, 1.0)
