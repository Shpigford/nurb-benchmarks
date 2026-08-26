from nurb import *
from math import cos, sin, pi, radians


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    shaft_fit=0.6,
    knob_width=29.2,
    lobe_count=6,
    lobe_reach=2.2,
    knob_height=14.0,
    bore_floor=2.0,
    draft=False,
):
    """A replacement valve knob that presses onto a D-shaped stem.

    shaft_diameter: how wide the valve stem is across its round side
    shaft_across_flat: how far it measures from the flat to the round side
    shaft_fit: extra room the bore leaves around the stem, total on the opening
    knob_width: how far across the knob is at its narrowest
    lobe_count: how many finger lobes run up the outside
    lobe_reach: how far each lobe stands proud of the knob body
    knob_height: how tall the knob is
    bore_floor: how much solid plastic sits under the bore
    """
    bore_radius = (shaft_diameter + shaft_fit) / 2.0
    bore_flat = shaft_across_flat + shaft_fit
    hub_radius = knob_width / 2.0

    if bore_flat >= 2.0 * bore_radius:
        reject(
            "shaft_across_flat has to be under shaft_diameter for a D-shaft: "
            f"give it something below {shaft_diameter:.1f}",
            param="shaft_across_flat",
        )
    if hub_radius - bore_radius < 3.0:
        reject(
            f"knob_width {knob_width:.1f} leaves under 3mm of wall around the bore: "
            f"raise it above {2.0 * (bore_radius + 3.0):.1f}",
            param="knob_width",
        )
    if knob_height - bore_floor < 10.5:
        reject(
            f"knob_height {knob_height:.1f} gives the stem under 10.5mm of bore: "
            f"raise it above {bore_floor + 10.5:.1f}",
            param="knob_height",
        )

    body = extrude(Circle(hub_radius), knob_height)

    lobe_radius = lobe_reach * 1.6
    for i in range(lobe_count):
        a = 2.0 * pi * i / lobe_count
        centre = (hub_radius + lobe_reach - lobe_radius)
        lobe = extrude(
            Pos(centre * cos(a), centre * sin(a)) * Circle(lobe_radius),
            knob_height,
        )
        body = body + lobe

    # D bore: a round pocket with one side planed off, the flat facing +X.
    bore = extrude(Circle(bore_radius), knob_height)
    flat_offset = bore_flat - bore_radius
    planer = Pos(flat_offset + bore_radius, 0, 0) * Box(
        2.0 * bore_radius, 4.0 * bore_radius, 4.0 * knob_height
    )
    bore = bore - planer
    body = body - Pos(0, 0, bore_floor) * bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    top = body.bounding_box().max.Z
    mouth = bore_radius + lobe_radius

    def outside_top(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 1e-6:
            return False
        # leave the bore mouth alone: it is the mating geometry
        return max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y)) > mouth

    keep = body.edges().filter_by(outside_top)
    return polish(body, keep, 1.0)
