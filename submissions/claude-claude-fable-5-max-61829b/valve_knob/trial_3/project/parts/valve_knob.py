from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    stem_clearance=0.32,
    grip_width=29.0,
    corner_radius=6.0,
    knob_height=14.0,
    draft=False,
):
    """Replacement knob for the valve's D-shaft stem, printed socket-up.

    shaft_diameter: how wide the valve stem is across its round side
    shaft_across_flat: how far the stem's flat face is from its round side
    stem_clearance: extra gap between the stem and its socket
    grip_width: how wide the knob is across its flat sides
    corner_radius: how round the knob's corners are
    knob_height: how tall the knob stands
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}: a D-shaft's flat has to cut into the circle",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter / 2:
        reject(
            f"shaft_across_flat {shaft_across_flat} cuts past the stem's centerline: "
            f"keep it above {shaft_diameter / 2:.1f}",
            param="shaft_across_flat",
        )
    if stem_clearance < 0.1:
        reject(
            f"stem_clearance {stem_clearance} is a bind, not a fit: printed bores "
            "come out small and vary by machine, keep it at 0.1 or more",
            param="stem_clearance",
        )
    if stem_clearance > 0.45:
        reject(
            f"stem_clearance {stem_clearance} is past the free-fit line: the knob "
            "would rattle on the stem instead of steering it, keep it under 0.45",
            param="stem_clearance",
        )

    bore_radius = shaft_diameter / 2 + stem_clearance
    flat_wall = shaft_across_flat - shaft_diameter / 2 + stem_clearance
    floor = 3.0
    socket_depth = knob_height - floor

    if knob_height < 13.0:
        reject(
            f"knob_height {knob_height} cannot hold 10mm of stem engagement over a "
            "3mm floor: keep it at 13.0 or more",
            param="knob_height",
        )
    if grip_width < 2 * (bore_radius + 3.0):
        reject(
            f"grip_width {grip_width} leaves under 3mm of wall around the "
            f"{2 * bore_radius:.1f} socket: raise it above "
            f"{2 * (bore_radius + 3.0):.1f}",
            param="grip_width",
        )
    if corner_radius < 0.5:
        reject(
            f"corner_radius {corner_radius} is too sharp to build or to hold: "
            "keep it at 0.5 or more",
            param="corner_radius",
        )
    if corner_radius > 0.7 * grip_width / 2:
        reject(
            f"corner_radius {corner_radius} makes the grip nearly round: the corners "
            "no longer stand proud of the flats and wet hands spin on it, keep it "
            f"under {0.7 * grip_width / 2:.1f}",
            param="corner_radius",
        )

    body = extrude(RectangleRounded(grip_width, grip_width, corner_radius), knob_height)

    # The stem's flat faces +X, so the socket keeps its flat wall on that side.
    socket = Circle(bore_radius) - Pos(flat_wall + bore_radius, 0) * Rectangle(
        2 * bore_radius, 3 * bore_radius
    )
    body -= Pos(0, 0, floor) * extrude(socket, socket_depth)

    if draft:
        return body
    # Chamfer the top rim only: the bed rim stays square, and the socket is a
    # mating mouth, so everything within reach of the bore stays sharp.
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and max(
            abs(e.bounding_box().min.X),
            abs(e.bounding_box().max.X),
            abs(e.bounding_box().min.Y),
            abs(e.bounding_box().max.Y),
        )
        > bore_radius + 1.0
    )
    return polish(body, keep, 1.0)
