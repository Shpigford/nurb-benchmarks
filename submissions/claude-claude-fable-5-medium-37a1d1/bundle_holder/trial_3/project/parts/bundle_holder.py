from nurb import *
import math


@part
def bundle_holder(bundle_diameter=8.0, length=10.0, wall=1.2, back_thickness=2.0,
                  screw_tab_thickness=3.0, clearance=0.4, draft=False):
    """Wall clip for a horizontal cable bundle: a closed teardrop tunnel with a screw tab above.

    bundle_diameter: how thick the cable bundle is
    length: how long the clip is along the bundle
    wall: thickness of the plastic around the tunnel
    back_thickness: thickness of the flat back behind the tunnel
    screw_tab_thickness: thickness of the tab the screw passes through
    clearance: extra room around the bundle so it slides in
    """
    r = (bundle_diameter + 2 * clearance) / 2  # tunnel radius
    tunnel_h = r + r * math.sqrt(2)             # teardrop: circle plus 45 deg roof
    body_w = back_thickness + 2 * r + wall      # along X (away from wall)
    body_h = wall + tunnel_h + wall             # along Z
    cz = wall + r                               # tunnel centre height
    cx = back_thickness + r

    # Lower block with the tunnel; back face on the YZ plane at X=0.
    block = Pos(body_w / 2, length / 2, body_h / 2) * Box(body_w, length, body_h)
    circle = Pos(cx, length / 2, cz) * Rot(90, 0, 0) * Cylinder(r, length + 2)
    # 45-degree roof so the tunnel ceiling prints without support.
    roof = Pos(cx, length / 2, cz) * Rot(0, 45, 0) * Box(r * math.sqrt(2), length + 2, r * math.sqrt(2))
    block = block - circle - roof

    # Screw tab above the tunnel, thin enough that the head clears in +X.
    head_r = 4.2
    tab_h = 2 * head_r + 2.0
    tab = Pos(screw_tab_thickness / 2, length / 2, body_h + tab_h / 2) * Box(
        screw_tab_thickness, length, tab_h)
    screw_z = body_h + tab_h / 2
    bore = Pos(0, length / 2, screw_z) * Rot(0, 90, 0) * Cylinder(2.2, 20)
    body = (block + tab) - bore
    if draft:
        return body
    # Chamfer only outer convex edges: the front face and the tab top, away from
    # the tunnel and the tab junction where a chamfer would be cosmetic.
    top = body.bounding_box().max.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > 1e-6 and (
            e.bounding_box().min.X >= body_w - 1e-6 or e.bounding_box().min.Z >= top - 1e-6))
    return polish(body, keep, 0.6)
