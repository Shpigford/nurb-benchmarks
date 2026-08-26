from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_width=28.6,
    lobe_reach=17.5,
    knob_height=13.0,
    bore_depth=11.0,
    bore_clearance=0.6,
    draft=False,
):
    """A replacement valve knob that presses onto a D-shaped stem.

    shaft_diameter: how wide the valve stem measures across its round side
    shaft_across_flat: how far it measures from the flat to the round side
    knob_width: how wide the knob body is between the finger lobes
    lobe_reach: how far the finger lobes stand out from the centerline
    knob_height: how tall the knob is
    bore_depth: how deep the socket for the stem goes
    bore_clearance: how much slack the socket leaves around the stem
    """
    bore_dia = shaft_diameter + bore_clearance
    bore_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_dia / 2
    flat_offset = bore_flat - bore_radius

    if flat_offset >= bore_radius:
        reject(
            "shaft_across_flat is at or past the full diameter, so there is no flat "
            f"to grip: keep it under {shaft_diameter:.1f}",
            param="shaft_across_flat",
        )
    if knob_height - bore_depth < 2.0:
        reject(
            f"bore_depth {bore_depth} leaves under 2mm of floor under the stem: "
            f"raise knob_height above {bore_depth + 2.0:.1f}",
            param="bore_depth",
        )

    hub = extrude(Circle(knob_width / 2), knob_height)

    # Four finger lobes so wet hands can turn it; vertical, so they print unsupported.
    lobe_radius = 4.5
    lobe_centre = lobe_reach - lobe_radius
    for i in range(4):
        angle = 45.0 + i * 90.0
        pos = Pos(lobe_centre * cos(radians(angle)), lobe_centre * sin(radians(angle)))
        hub += pos * extrude(Circle(lobe_radius), knob_height)

    # The D-bore: a round socket with one side flattened, opening at the top face.
    profile = Circle(bore_radius) - Pos(
        flat_offset + bore_radius, 0
    ) * Rectangle(2 * bore_radius, 4 * bore_radius)
    body = hub - Pos(0, 0, knob_height - bore_depth) * extrude(profile, bore_depth)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    bore_wall = bore_radius + 0.2
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 > bore_wall
    )
    return polish(body, keep, 1.0)
