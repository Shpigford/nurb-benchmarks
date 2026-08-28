from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    shaft_length=measured("shaft_length"),
    bore_clearance=0.6,
    cap_thickness=3.0,
    grip_width=29.2,
    lobe_height=3.8,
    lobe_width=6.8,
    lobe_count=4,
    draft=False,
):
    """A replacement handle for a valve with a D-shaped stem.

    Modelled bore-up, the way it prints: the bore opens straight up on the
    centerline with the stem's flat toward +X, and the knob flips over onto the
    stem in use, so the face on the bed is the crown you grip.

    shaft_diameter: how far across the round side of the valve stem measures
    shaft_across_flat: from the stem's flat across to the round side opposite it
    shaft_length: how far the stem stands proud of the valve body
    bore_clearance: how much wider than the stem the bore is cut, all the way round
    cap_thickness: the plastic closing the end of the bore, the crown of the knob in use
    grip_width: how far across the knob measures at its narrow waist
    lobe_height: how far each finger lobe stands out past the waist
    lobe_width: how wide across each finger lobe is
    lobe_count: how many finger lobes go round the knob
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}, so the flat takes nothing off and there is no D to "
            f"drive: measure across the flat again",
            param="shaft_across_flat",
        )

    bore_radius = (shaft_diameter + bore_clearance) / 2
    # The flat wall of the bore, offset from the axis on +X. Both measurements move it:
    # across-flat sets where it sits, diameter sets where it sits relative to.
    flat_offset = shaft_across_flat + bore_clearance - bore_radius
    bore_depth = shaft_length + 0.5  # the stem tip never bottoms out in the bore
    height = bore_depth + cap_thickness

    waist = grip_width / 2
    if waist - bore_radius < 2.0:
        reject(
            f"grip_width {grip_width} leaves {waist - bore_radius:.1f}mm of wall around "
            f"a {bore_radius * 2:.1f}mm bore: raise it above "
            f"{(bore_radius + 2.0) * 2:.1f}",
            param="grip_width",
        )
    if lobe_count < 3:
        reject(
            f"lobe_count {lobe_count} cannot spread grip round the knob: use 3 or more",
            param="lobe_count",
        )

    lobe_radius = lobe_width / 2
    lobe_centre = waist + lobe_height - lobe_radius
    if lobe_centre - lobe_radius >= waist:
        reject(
            f"lobe_width {lobe_width} is too narrow to reach {lobe_height}mm out of the "
            f"waist and still meet it: widen it past {2 * lobe_height:.1f}",
            param="lobe_width",
        )

    outline = Circle(waist)
    for i in range(lobe_count):
        outline += Rot(0, 0, 360.0 * i / lobe_count) * Pos(lobe_centre, 0) * Circle(lobe_radius)
    body = extrude(outline, height)

    # The D bore, cut from the top face down and run out through it so the mouth is
    # full section. Nothing is chamfered here: a lead-in at a mating mouth prints as
    # compound slivers and this bore is the one fit on the part.
    d = Circle(bore_radius) - Pos(flat_offset + bore_radius, 0) * Rectangle(
        2 * bore_radius, 2 * bore_radius
    )
    body -= Pos(0, 0, cap_thickness) * extrude(d, bore_depth + 1.0)

    if draft:
        return body

    # Polish the top rim only: the bed face carries the crown and a chamfer lying in it
    # lays a knife edge into the first layer, and the bore mouth is fit-critical.
    top = body.bounding_box().max.Z

    def rim(e):
        b = e.bounding_box()
        if b.min.Z < top - 1e-3:
            return False
        reach = max(abs(b.min.X), abs(b.max.X), abs(b.min.Y), abs(b.max.Y))
        return reach > waist * 0.5

    return polish(body, body.edges().filter_by(rim), 1.0)
