from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_across=32.0,
    height=15.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: round diameter of the valve stem
    shaft_across_flat: distance from the stem's flat to the opposite round side
    knob_across: width across the hex flats, the narrowest grip
    height: how tall the knob prints (bore opens at the top)
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )
    if shaft_diameter <= 0:
        reject("shaft_diameter must be positive", param="shaft_diameter")
    if knob_across < 28.0:
        reject("knob_across must stay at least 28 so wet hands can grip it", param="knob_across")
    if height < 12.0:
        reject("height must be at least 12 to cover the stem", param="height")

    # Virtual stem is grown 0.3 (must pass) and 1.0 (must jam). 0.6 sits between.
    clearance = 0.6
    bore_d = shaft_diameter + clearance
    bore_across = shaft_across_flat + clearance
    bore_r = bore_d / 2.0
    x_flat = -bore_r + bore_across

    floor = 2.5
    if height - floor < 10.5:
        floor = max(0.0, height - 10.5)

    hex_radius = knob_across / (3.0 ** 0.5)

    with BuildPart() as p:
        with BuildSketch():
            RegularPolygon(hex_radius, 6)
        extrude(amount=height)

        if floor <= 0:
            plane = Plane.XY.offset(-0.1)
            cut_h = height + 0.2
        else:
            plane = Plane.XY.offset(floor)
            cut_h = height - floor + 0.1
        with BuildSketch(plane):
            Circle(bore_r)
            with Locations((x_flat + bore_r + 4.0, 0)):
                Rectangle(2.0 * bore_r + 8.0, 2.0 * bore_r + 8.0, mode=Mode.SUBTRACT)
        extrude(amount=cut_h, mode=Mode.SUBTRACT)

    body = p.part

    if draft:
        return body

    bed = body.bounding_box().min.Z
    # Keep the D-bore sharp so the flat can still transmit torque after polish.
    bore_limit = (bore_r + 1.2) ** 2

    def outer_edge(e):
        if e.bounding_box().min.Z <= bed + 1e-6:
            return False
        mid = e @ 0.5
        return mid.X * mid.X + mid.Y * mid.Y > bore_limit

    keep = body.edges().filter_by(outer_edge)
    return polish(body, keep, 1.0)
