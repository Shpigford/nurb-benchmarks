from math import cos, radians

from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    height=14.0,
    grip_width=32.0,
    draft=False,
):
    """Replacement D-shaft valve knob, printed bore-up so the stem drops in from above.

    shaft_diameter: round diameter of the valve stem.
    shaft_across_flat: stem size from the flat face to the opposite round side.
    height: how tall the knob prints (bore opens at the top).
    grip_width: distance across the hexagonal flats.
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than the round diameter",
            param="shaft_across_flat",
        )
    if height < 12.0:
        reject("height must be at least 12 mm so the stem is covered", param="height")
    if grip_width < 28.0:
        reject("grip_width must stay at least 28 mm across", param="grip_width")

    # 0.5 mm over the measured stem: a 0.3 mm virtual stem still clears,
    # a 1.0 mm virtual stem and a 20-degree twist both jam.
    bore_dia = shaft_diameter + 0.5
    bore_across = shaft_across_flat + 0.5
    bore_r = bore_dia / 2.0
    flat_x = bore_across - bore_r

    hex_r = (grip_width / 2.0) / cos(radians(30.0))
    body = extrude(RegularPolygon(hex_r, 6), amount=height)

    bore = Cylinder(bore_r, height + 4.0)
    cap = Box(bore_r * 4.0, bore_r * 4.0, height + 6.0)
    cap = cap.moved(Location((flat_x + bore_r * 2.0, 0, 0)))
    d_bore = (bore - cap).moved(Location((0, 0, height / 2.0)))
    body = body - d_bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = (body.edges() - concave_edges(body)).filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05
    )
    return polish(body, keep, 1.0)
