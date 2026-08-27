import math

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    height=16.0,
    valley_radius=15.0,
    lobe_radius=18.0,
    bore_clearance=0.6,
    bore_depth=13.0,
    draft=False,
):
    """A lobed replacement knob with a print-up D-shaft socket.

    shaft_diameter: diameter of the valve stem.
    shaft_across_flat: distance from the stem flat to its opposite round side.
    height: overall height of the knob.
    valley_radius: radius at the valleys between grip lobes.
    lobe_radius: radius at each grip lobe.
    bore_clearance: total fit allowance added to each shaft measurement.
    bore_depth: depth of the socket down from the top face.
    """
    if shaft_diameter <= 0 or shaft_across_flat <= 0:
        reject("shaft dimensions must be positive", param="shaft_diameter")
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter for a D shaft",
            param="shaft_across_flat",
        )
    if height < 12.0:
        reject("height must be at least 12.0mm for the valve stem", param="height")
    if valley_radius <= 0 or lobe_radius <= valley_radius:
        reject(
            "lobe_radius must be greater than the positive valley_radius",
            param="lobe_radius",
        )
    if bore_clearance <= 0:
        reject("bore_clearance must be positive so the grown stem can pass", param="bore_clearance")
    if bore_depth <= 10.0 or bore_depth >= height:
        reject("bore_depth must be between 10.0mm and the top face", param="bore_depth")

    # Alternating radii make six broad, usable lobes without introducing
    # overhanging grip features.  The first point is on +X, matching the D
    # socket's reference direction.
    points = []
    for index in range(12):
        angle = math.radians(index * 30.0)
        radius = lobe_radius if index % 2 == 0 else valley_radius
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    body = extrude(Polygon(*points), amount=height)

    # The D socket is a cylinder clipped at the +X flat.  Across-flat is the
    # distance from the -X round extreme to that clipping plane.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_bottom = height - bore_depth
    bore = Pos(0, 0, bore_bottom) * Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    clip_min_x = -bore_radius - 2.0
    clip = Pos(
        (clip_min_x + bore_flat_x) / 2.0,
        0,
        bore_bottom + bore_depth / 2.0,
    ) * Box(
        bore_flat_x - clip_min_x,
        2.0 * bore_radius + 4.0,
        bore_depth,
    )
    socket = bore & clip
    result = body - socket

    if draft:
        return result

    # Keep the fit-critical socket edges and bed face untouched.  Polish only
    # the exposed, convex outside edges; the body remains a single solid.
    bed = result.bounding_box().min.Z
    concave = concave_edges(result)
    exposed = result.edges().filter_by(
        lambda edge: edge not in concave
        and edge.bounding_box().min.Z > bed + 0.01
        and edge.bounding_box().max.Z > bed + 0.01
    )
    return polish(result, exposed, 1.0)
