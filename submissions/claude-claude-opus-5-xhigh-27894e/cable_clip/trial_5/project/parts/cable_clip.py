from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    edge_chamfer=1.2,
    draft=False,
):
    """A screw-down clip that traps a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra width in the channel so the bundle drops in
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the channel and under the tab
    clip_length: how far the clip reaches along the cable
    tab_length: how far the screw tab sticks out past the wall
    screw_hole_width: how wide the screw hole through the tab is
    edge_chamfer: how much is taken off the outside edges
    """
    if bundle_diameter < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a channel too narrow to print"
            " or to lay a cable into: raise it above 2",
            param="bundle_diameter",
        )
    if edge_chamfer < 0.8:
        reject(
            f"edge_chamfer {edge_chamfer} prints as a defect rather than a facet:"
            " raise it to 0.8 or above",
            param="edge_chamfer",
        )
    if screw_hole_width + 2 * wall_thickness > tab_length:
        reject(
            f"screw_hole_width {screw_hole_width} leaves under {wall_thickness}mm of tab"
            f" around the bore: raise tab_length above {screw_hole_width + 2 * wall_thickness}",
            param="screw_hole_width",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    wall_out = body_width / 2          # outside of both channel walls
    channel_out = channel_width / 2    # inside of both channel walls
    tab_end = wall_out + tab_length    # far end of the mounting tab
    hole_x = wall_out + tab_length / 2

    # One closed profile in XZ, extruded along Y: the channel, its two walls and the
    # tab all come out of a single prism, so there is no fused seam to chamfer by
    # accident and the channel floor stays one face.
    outline = [
        (-wall_out, 0.0),
        (tab_end, 0.0),
        (tab_end, base_thickness),
        (wall_out, base_thickness),
        (wall_out, height),
        (channel_out, height),
        (channel_out, base_thickness),
        (-channel_out, base_thickness),
        (-channel_out, height),
        (-wall_out, height),
    ]
    body = extrude(
        Plane.XZ * Polygon(*outline, align=None), amount=clip_length / 2, both=True
    )
    body -= Pos(hole_x, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness * 2
    )

    if draft:
        return body

    tol = 1e-6
    concave = [e.center() for e in concave_edges(body)]

    def keep(edge):
        box = edge.bounding_box()
        # Nothing lying in the bed face: a chamfer there buys nothing.
        if box.max.Z < tol:
            return False
        # Nothing inside the channel. The floor stays one flat face the full width and
        # the mouth gets no lead-in, so the bundle sees square corners all the way down.
        if (
            box.min.Z > base_thickness - tol
            and box.min.X > -channel_out - tol
            and box.max.X < channel_out + tol
        ):
            return False
        # Nothing on the channel rim's ends either. The edge itself sits outside the
        # channel, but its chamfer caps against the inner wall and clips that face's top
        # corner, which is a bevel inside the channel by another route.
        if box.min.Z > height - tol and box.max.Y - box.min.Y < tol:
            return False
        # Nothing on the screw bore: the tab top is what the screw head bears on.
        if (
            box.min.X > hole_x - screw_hole_width / 2 - tol
            and box.max.X < hole_x + screw_hole_width / 2 + tol
            and box.min.Y > -screw_hole_width / 2 - tol
            and box.max.Y < screw_hole_width / 2 + tol
        ):
            return False
        # Never a concave edge: a chamfer there is a wedge, not a corner taken off.
        return not any((edge.center() - c).length < tol for c in concave)

    return polish(body, body.edges().filter_by(keep), edge_chamfer)
