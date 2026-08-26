from math import cos, sin, tau

from nurb import *

# Print clearance on the D-bore: larger than the 0.3 mm stem that must pass,
# smaller than the 1.0 mm stem that must jam.
_BORE_CLEARANCE = 0.65
_FLOOR = 2.5


def _d_profile(diameter, across_flat):
    """D-section: circle with the flat facing +X (material on the -X side)."""
    radius = diameter / 2.0
    flat_x = across_flat - radius
    circle = Circle(radius)
    cap = Pos(flat_x, 0) * Rectangle(
        diameter, diameter, align=(Align.MIN, Align.CENTER)
    )
    return circle - cap


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_height=14.5,
    grip_width=30.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem. Prints bore-up.

    shaft_diameter: round width of the stem
    shaft_across_flat: stem thickness from the flat to the round side
    knob_height: overall printed height, floor plus bore
    grip_width: waist across the hub, between the lobes
    """
    if shaft_diameter < 4.0:
        reject(
            "shaft_diameter is under 4mm: too small for a printable D-bore",
            param="shaft_diameter",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter to leave a flat",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= 0.0:
        reject("shaft_across_flat must be positive", param="shaft_across_flat")
    if knob_height < 12.0:
        reject("knob_height must be at least 12mm", param="knob_height")
    if grip_width < 28.0:
        reject(
            "grip_width must be at least 28mm so wet hands can turn it",
            param="grip_width",
        )

    hub_radius = grip_width / 2.0
    lobe_offset = hub_radius * 0.80
    lobe_radius = hub_radius * 0.47

    outline = Circle(hub_radius)
    for i in range(5):
        angle = i * tau / 5
        outline = outline + Pos(
            lobe_offset * cos(angle), lobe_offset * sin(angle)
        ) * Circle(lobe_radius)

    body = extrude(outline, amount=knob_height)

    bore_d = shaft_diameter + _BORE_CLEARANCE
    bore_af = shaft_across_flat + _BORE_CLEARANCE
    floor = min(_FLOOR, knob_height - 10.0)
    cutter = extrude(_d_profile(bore_d, bore_af), amount=knob_height - floor + 1.0)
    body = body - Pos(0, 0, floor) * cutter

    if draft:
        return body

    bed = body.bounding_box().min.Z
    bore_limit = (bore_d / 2.0) + 1.0

    def keep_edge(edge):
        if edge.bounding_box().min.Z <= bed + 1e-6:
            return False
        mid = edge.bounding_box().center()
        return mid.X * mid.X + mid.Y * mid.Y > bore_limit * bore_limit

    keep = body.edges().filter_by(keep_edge) - concave_edges(body)
    return polish(body, keep, 1.0)
