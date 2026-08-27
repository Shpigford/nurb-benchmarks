from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A support-free six-lobed replacement knob for a D-shaped valve stem.

    shaft_diameter: the full round diameter of the valve stem
    shaft_across_flat: the distance from the stem's flat to its opposite round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if shaft_across_flat <= shaft_diameter / 2.0:
        reject(
            "shaft_across_flat must be greater than half of shaft_diameter",
            param="shaft_across_flat",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter to form a D-shaft",
            param="shaft_across_flat",
        )

    height = 16.0
    valley_radius = 15.0
    lobe_radius = 18.5
    lobe_count = 6

    # Alternating radii make broad, easy-to-grip lobes while leaving a large,
    # uninterrupted first layer. Starting at +X keeps a lobe aligned with the flat.
    outline_points = []
    for index in range(lobe_count * 2):
        angle = index * pi / lobe_count
        radius = lobe_radius if index % 2 == 0 else valley_radius
        outline_points.append((radius * cos(angle), radius * sin(angle)))

    body = extrude(Polygon(*outline_points), height)

    # The 0.5 mm dimensional allowance clears the +0.3 mm fit probe with
    # 0.2 mm of real diametral/flat clearance, but rejects the +1.0 mm probe.
    bore_diameter = shaft_diameter + 0.5
    bore_across_flat = shaft_across_flat + 0.5
    bore_radius = bore_diameter / 2.0
    flat_x = bore_across_flat - bore_radius

    round_bore = Circle(bore_radius)
    flat_half_plane = Rectangle(
        2.0 * bore_radius + 2.0,
        2.0 * bore_radius + 2.0,
        align=(Align.MAX, Align.CENTER),
    ).translate((flat_x, 0.0))
    bore_profile = round_bore & flat_half_plane

    # The 12.5 mm blind depth accepts the entire 12 mm proud stem while
    # preserving a 3.5 mm floor for a strong, bed-flat print.
    bore_depth = 12.5
    bore = extrude(bore_profile, bore_depth + 0.2).translate(
        (0.0, 0.0, height - bore_depth)
    )
    body = body - bore

    if draft:
        return body

    # Chamfer only the handled outer top rim. The bed face and every edge of
    # the fit-critical D-bore remain exact and sharp.
    top = body.bounding_box().max.Z
    outer_top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > top - 0.01
        and edge.center().X * edge.center().X + edge.center().Y * edge.center().Y > 100.0
    )
    return polish(body, outer_top_edges, 1.0)
