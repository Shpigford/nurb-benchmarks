from math import cos, hypot, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.65,
    bore_depth=11.0,
    grip_diameter=29.0,
    lobe_diameter=7.5,
    lobe_count=4,
    height=14.0,
    chamfer_size=1.0,
    draft=False,
):
    """A lobed replacement knob for the valve stem, printed bore-up and flipped onto the stem.

    shaft_diameter: the valve stem measured across its round sides
    shaft_across_flat: the valve stem measured from the flat to the round side
    bore_clearance: extra room in the stem hole so it slides on without rattling
    bore_depth: how deep the stem sinks into the knob
    grip_diameter: the round core of the knob, measured across
    lobe_diameter: how thick each grip lobe is
    lobe_count: how many grip lobes ring the knob
    height: how tall the knob stands
    chamfer_size: the edge break on the top rim
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}: the stem would have no flat and the knob would spin on it",
            param="shaft_across_flat",
        )
    if bore_clearance < 0.1:
        reject(
            f"bore_clearance {bore_clearance} is under 0.1, which is a bind that varies "
            "by machine rather than a tighter fit: keep it at 0.1 or more",
            param="bore_clearance",
        )
    if grip_diameter < shaft_diameter + bore_clearance + 4.0:
        reject(
            f"grip_diameter {grip_diameter} leaves under 2mm of wall around the "
            f"{shaft_diameter + bore_clearance:.2f} stem hole: raise it above "
            f"{shaft_diameter + bore_clearance + 4.0:.2f}",
            param="grip_diameter",
        )
    if bore_depth > height - 2.0:
        reject(
            f"bore_depth {bore_depth} leaves under 2mm of floor in a knob {height} tall: "
            f"lower it below {height - 2.0:.2f} or raise height",
            param="bore_depth",
        )

    bore_dia = shaft_diameter + bore_clearance
    bore_flat = shaft_across_flat + bore_clearance

    grip = Circle(grip_diameter / 2.0)
    for i in range(lobe_count):
        a = radians(i * 360.0 / lobe_count)
        grip += Pos(
            cos(a) * grip_diameter / 2.0, sin(a) * grip_diameter / 2.0
        ) * Circle(lobe_diameter / 2.0)
    body = extrude(grip, height)

    # D-bore: the stem's flat faces +X, so the socket keeps its flat wall there.
    flat_x = bore_flat - bore_dia / 2.0
    socket = Circle(bore_dia / 2.0) - Pos(flat_x + bore_dia / 2.0, 0) * Rectangle(
        bore_dia, bore_dia
    )
    body -= Pos(0, 0, height - bore_depth) * extrude(socket, bore_depth)

    if draft:
        return body

    # Keep sharp: the bed rim, the concave lobe junctions (both reach the bed), and
    # the bore mouth, which is mating geometry. What remains is the top rim.
    bed = body.bounding_box().min.Z
    guard = (bore_dia / 2.0 + grip_diameter / 2.0) / 2.0
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and hypot(e.center().X, e.center().Y) > guard
    )
    return polish(body, keep, chamfer_size)
