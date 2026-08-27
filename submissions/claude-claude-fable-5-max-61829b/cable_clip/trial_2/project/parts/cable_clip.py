import math

from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    chamfer_size=1.0,
    draft=False,
):
    """A screw-down clip that holds a cable bundle in an open-top channel.

    bundle_diameter: how wide the cable bundle is, measured across it
    cable_clearance: extra channel width on top of the bundle so it drops in
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable; the screw tab is the same
    length: how long the clip is along the cable
    tab_length: how far the screw tab reaches out from the side of the clip
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: size of the chamfer taken off the exposed edges
    """
    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    height = base_thickness + channel_depth
    half_channel = channel_width / 2
    outer = half_channel + wall_thickness       # x of the outside of each wall
    tab_end = outer + tab_length                # x of the far end of the tab
    hole_x = outer + tab_length / 2             # the hole sits in the middle of the tab
    hole_r = screw_hole_width / 2

    if channel_width <= 0:
        reject("the channel would be closed: raise bundle_diameter", param="bundle_diameter")
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed hole needs "
            "to open: raise it to at least 2.0",
            param="screw_hole_width",
        )
    if (tab_length - screw_hole_width) / 2 < 2.0 - 1e-6:
        reject(
            f"tab_length {tab_length} leaves under 2mm beside the {screw_hole_width}mm "
            f"screw hole: raise it to at least {screw_hole_width + 4.0:.1f}",
            param="tab_length",
        )
    if (length - screw_hole_width) / 2 < 2.0 - 1e-6:
        reject(
            f"length {length} leaves under 2mm beside the {screw_hole_width}mm screw "
            f"hole: raise it to at least {screw_hole_width + 4.0:.1f}",
            param="length",
        )
    if 0 < chamfer_size < 0.8:
        reject("a chamfer under 0.8mm prints as a defect: use 0 for none or 0.8 and up",
               param="chamfer_size")
    if chamfer_size >= min(wall_thickness, base_thickness):
        reject(
            f"chamfer_size {chamfer_size} is as big as the wall or base it sits on: "
            f"keep it under {min(wall_thickness, base_thickness)}",
            param="chamfer_size",
        )

    # The whole clip is one profile in the XZ plane, drawn counter-clockwise from the
    # bottom-left corner: base and tab along the bed, up the tab's end, in across the
    # tab top, up the outside of the right wall, down into the channel, across the
    # floor, up the left wall, and back down the outside of the left wall.
    profile = [
        (-outer, 0),
        (tab_end, 0),
        (tab_end, base_thickness),
        (outer, base_thickness),
        (outer, height),
        (half_channel, height),
        (half_channel, base_thickness),
        (-half_channel, base_thickness),
        (-half_channel, height),
        (-outer, height),
    ]
    body = extrude(Plane.XZ * make_face(Polyline(*profile, close=True)), amount=length / 2, both=True)

    hole = Cylinder(hole_r, base_thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body - hole.moved(Location((hole_x, 0, 0)))

    if draft or chamfer_size == 0:
        return body

    # Polish: name what must stay sharp, then let `polish` chamfer whatever lands.
    eps = 1e-3
    bed = body.bounding_box().min.Z

    def in_bed(e):
        return e.bounding_box().max.Z < bed + eps

    def in_channel(e):
        # Anything touching the channel's floor or inner faces is fit geometry.
        b = e.bounding_box()
        return (
            b.max.X > -half_channel - eps
            and b.min.X < half_channel + eps
            and b.max.Z > base_thickness - eps
        )

    def in_hole(e):
        c = e.bounding_box().center()
        return math.hypot(c.X - hole_x, c.Y) <= hole_r + eps

    def across(e):
        # Runs along X, so it lies in one of the cut ends. The ends stay square: the
        # short wall-top edges would clip the channel's inner-face corners, and the
        # tab's long top edges would put a third chamfer on each far tab corner,
        # whose ~0.87mm2 corner triangles the sliver rule counts (measured: two
        # findings). See the card's Don't.
        b = e.bounding_box()
        return (b.max.X - b.min.X) > eps and (b.max.Y - b.min.Y) < eps and (b.max.Z - b.min.Z) < eps

    keep = body.edges().filter_by(
        lambda e: not (in_bed(e) or in_channel(e) or in_hole(e) or across(e))
    ) - concave_edges(body)
    return polish(body, keep, chamfer_size)
