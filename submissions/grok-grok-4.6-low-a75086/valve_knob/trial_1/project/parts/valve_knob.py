from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    height=16.0,
    grip_width=30.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: round diameter of the valve stem
    shaft_across_flat: stem width from the flat to the round side
    height: overall knob height as printed
    grip_width: distance across the hex flats
    """
    clearance = 0.5
    bore_r = (shaft_diameter + clearance) / 2
    bore_af = shaft_across_flat + clearance
    # D-flat faces +X. Across-flat is flat-to-round, so the plane sits at
    # (across-flat) minus the circle radius.
    flat_x = bore_af - bore_r

    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )
    if flat_x <= 0.2:
        reject(
            "bore flat would pass the centerline; raise shaft_across_flat",
            param="shaft_across_flat",
        )
    if grip_width < shaft_diameter + clearance + 8.0:
        reject(
            "grip_width is too small to leave wall around the stem",
            param="grip_width",
        )
    if height < 12.0:
        reject("height must be at least 12 so the stem can seat", param="height")

    apothem = grip_width / 2
    vertex_r = apothem / ((3**0.5) / 2)

    body = extrude(RegularPolygon(vertex_r, 6), height)

    d_profile = Circle(bore_r) - Pos(flat_x + bore_r, 0) * Rectangle(
        2 * bore_r, 4 * bore_r
    )
    hole = extrude(d_profile, height + 2).move(Location((0, 0, -1)))
    body = body - hole

    if draft:
        return body

    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.2
        and (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 > bore_r + 1.5
    )
    return polish(body, keep, 1.0)
