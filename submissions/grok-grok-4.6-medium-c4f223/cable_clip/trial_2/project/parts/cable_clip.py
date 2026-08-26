from nurb import *

WALL = 2.4
BASE = 3.0
LENGTH = 12.0
TAB_LENGTH = 10.0
TAB_THICKNESS = 3.0
HOLE_DIA = 4.2
CHANNEL_CLEARANCE = 0.4


@part
def cable_clip(bundle_diameter=float(measured("bundle_diameter")), draft=False):
    """Screw-down clip that holds a cable bundle in an open-top channel.

    bundle_diameter: measured diameter of the cable bundle the channel holds
    """
    if bundle_diameter < 1.0:
        reject(
            "bundle_diameter 1.0mm is the smallest channel that still prints; raise it",
            param="bundle_diameter",
        )

    channel_width = bundle_diameter + CHANNEL_CLEARANCE
    channel_depth = bundle_diameter
    body_width = WALL + channel_width + WALL
    body_height = BASE + channel_depth

    body = Box(body_width, LENGTH, body_height, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = Box(
        TAB_LENGTH, LENGTH, TAB_THICKNESS, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    tab = tab.moved(Location((body_width, 0, 0)))
    clip = body + tab

    channel = Box(
        channel_width,
        LENGTH + 2.0,
        channel_depth + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).moved(Location((WALL, -1.0, BASE)))
    clip = clip - channel

    hole = Cylinder(
        HOLE_DIA / 2.0,
        TAB_THICKNESS + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((body_width + TAB_LENGTH / 2.0, LENGTH / 2.0, -1.0)))
    clip = clip - hole

    if draft:
        return clip

    bed = clip.bounding_box().min.Z
    floor_z = BASE
    left_x = WALL
    right_x = WALL + channel_width
    concave = concave_edges(clip)

    def is_channel_inner_face(face):
        bb = face.bounding_box()
        if abs(bb.min.Z - floor_z) < 0.05 and abs(bb.max.Z - floor_z) < 0.05:
            mid_x = 0.5 * (bb.min.X + bb.max.X)
            return left_x + 0.05 < mid_x < right_x - 0.05
        if bb.max.Z > floor_z + 0.5:
            if abs(bb.min.X - left_x) < 0.05 and abs(bb.max.X - left_x) < 0.05:
                return True
            if abs(bb.min.X - right_x) < 0.05 and abs(bb.max.X - right_x) < 0.05:
                return True
        return False

    inner_faces = clip.faces().filter_by(is_channel_inner_face)
    hole_faces = clip.faces().filter_by(GeomType.CYLINDER)
    skip = {e for f in list(inner_faces) + list(hole_faces) for e in f.edges()}
    skip.update(concave)

    def along_y(edge):
        bb = edge.bounding_box()
        return (
            bb.max.Y - bb.min.Y > LENGTH - 0.2
            and bb.max.X - bb.min.X < 0.2
            and bb.max.Z - bb.min.Z < 0.2
        )

    keep = clip.edges().filter_by(
        lambda e: e not in skip
        and e.bounding_box().min.Z > bed + 0.05
        and along_y(e)
    )
    return polish(clip, keep, 1.0)
