from nurb import *
import math


@part
def bundle_holder(bundle_diameter=8.0, draft=False):
    """A wall-mounted, support-free cable tunnel with a separate screw seat.

    bundle_diameter: measured width of the cable bundle; the passage adds 0.4 mm.
    """
    if bundle_diameter < 4.0:
        reject("bundle_diameter must be at least 4 mm", param="bundle_diameter")
    radius = (bundle_diameter + 0.4) / 2
    length = 10.6
    back = 2.6
    floor = 2.4
    left = back + 0.4
    middle = left + radius
    right = middle + radius
    center_height = floor + radius
    roof = center_height + radius * math.sqrt(2) + 0.15
    shoulder = roof - radius
    roof_thickness = 2.2 * math.sqrt(2)
    outside_right = right + 2.4
    outside_peak = roof + roof_thickness
    screw_height = outside_peak + 5.5
    height = screw_height + 5.5
    outline = Polygon(
        (0, 0), (outside_right, 0),
        (outside_right, outside_peak - (outside_right - middle)),
        (middle, outside_peak), (back, outside_peak - (middle - back)),
        (back, height), (0, height), align=None,
    )
    passage = Polygon(
        (left, floor), (right, floor), (right, shoulder),
        (middle, roof), (left, shoulder), align=None,
    )
    body = extrude(Plane.XZ * outline, amount=length / 2, both=True)
    body -= extrude(Plane.XZ * passage, amount=length / 2 + 1, both=True)
    bore = Pos(back / 2, 0, screw_height) * Cylinder(
        2.2, back + 2, rotation=(0, 90, 0)
    )
    body -= bore
    if draft:
        return body
    # Preserve the wall datum, screw-bearing face, and cable-contact surfaces.
    concave = concave_edges(body)
    edges = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > 0.01
        and e.bounding_box().min.X > back + 0.01
        and e.bounding_box().min.Z > shoulder + 0.01
        and e not in concave
    )
    return polish(body, edges, 1.0)
