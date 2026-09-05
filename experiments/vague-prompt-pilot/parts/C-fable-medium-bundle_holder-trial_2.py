from nurb import *

# Wall-mount J-hook for a cable bundle. The wall is the plane at min X (flat back
# face), the bundle runs along Y, down is -Z, and the part prints as mounted:
# every wall is vertical, the channel floor is solid to the bed, so no supports.

SCREW_CLEARANCE = 4.5  # M4 clearance hole, ISO 273 medium column
SCREW_WALL = 4.0       # a loaded hole earns a fastener diameter of wall


@part
def bundle_holder(
    channel_slack=1.0,
    holder_width=14.0,
    front_wall=3.0,
    back_thickness=4.0,
    lip_height=3.0,
    driver_gap=6.0,
    draft=False,
):
    """Wall hook that a cable bundle drops into from above, along the wall.

    channel_slack: extra channel width beyond the measured bundle, so cables slide
    holder_width: how wide the holder is along the cable run
    front_wall: thickness of the wall wrapping the front of the channel
    back_thickness: thickness of the plate the screw pulls against the wall
    lip_height: how far the front lip rises above the seated bundle
    driver_gap: room between the lip top and the screw for the screwdriver
    """
    bundle = measured("bundle_diameter")
    if channel_slack < 0.5:
        reject(
            f"channel_slack {channel_slack} is under the 0.5mm free-fit floor: "
            "the bundle would bind instead of sliding in",
            param="channel_slack",
        )
    if holder_width < SCREW_CLEARANCE + 2 * SCREW_WALL:
        reject(
            f"holder_width {holder_width} leaves under {SCREW_WALL}mm of material "
            f"beside the M4 hole: raise it to {SCREW_CLEARANCE + 2 * SCREW_WALL} or more",
            param="holder_width",
        )

    channel = bundle + channel_slack       # channel width, cables drop in along the wall
    radius = channel / 2.0
    floor = front_wall                     # material under the channel's round bottom
    seat_z = floor + radius                # centre of the cradle arc
    lip_z = floor + channel + lip_height   # top of the front wall
    screw_z = lip_z + driver_gap + SCREW_CLEARANCE / 2 + SCREW_WALL
    plate_top = screw_z + SCREW_CLEARANCE / 2 + SCREW_WALL
    reach = back_thickness + channel + front_wall  # how far the part leaves the wall

    plate = Box(
        back_thickness, holder_width, plate_top,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    hook = Box(
        reach, holder_width, lip_z,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    body = plate + hook

    # Channel: vertical slot off the plate's front face with a half-round cradle
    # at the bottom. Open at the top so the bundle slides down along the wall.
    slot = Pos(back_thickness, 0, seat_z) * Box(
        channel, holder_width + 2, lip_z - seat_z + 1,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    cradle = Pos(back_thickness + radius, 0, seat_z) * Rot(90, 0, 0) * Cylinder(
        radius, holder_width + 2
    )
    body -= slot + cradle

    # M4 clearance hole through the back plate, above the hook so the driver clears it.
    body -= Pos(-1, 0, screw_z) * Rot(0, 90, 0) * Cylinder(
        SCREW_CLEARANCE / 2, back_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    if draft:
        return body

    # Polish: skip the back face, the bed face, concave edges, and the channel
    # mouth (fit geometry gets no lead-in); chamfer greedily everywhere else.
    box = body.bounding_box()
    concave = set(concave_edges(body))
    channel_lo, channel_hi = back_thickness - 0.01, back_thickness + channel + 0.01

    def keepable(e):
        bb = e.bounding_box()
        if bb.max.X < box.min.X + 0.01:      # lies in the back face
            return False
        if bb.max.Z < box.min.Z + 0.01:      # lies in the bed face
            return False
        if e in concave:
            return False
        # channel mouth and walls: everything at channel X range below the lip
        if bb.min.X > channel_lo and bb.max.X < channel_hi and bb.max.Z < lip_z + 0.01:
            return False
        return True

    keep = body.edges().filter_by(keepable)
    return polish(body, keep, 1.0)
