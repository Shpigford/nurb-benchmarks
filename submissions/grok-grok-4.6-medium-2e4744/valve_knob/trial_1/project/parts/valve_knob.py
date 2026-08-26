from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_length=40.0,
    knob_width=32.0,
    knob_height=13.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: caliper reading across the round of the stem
    shaft_across_flat: caliper reading from the stem's flat to the round side
    knob_length: overall length of the grip, the long way
    knob_width: overall width of the grip, the short way
    knob_height: how tall the knob is
    """
    if shaft_diameter < 4.0:
        reject(
            f"shaft_diameter {shaft_diameter} is under 4mm: raise it so the bore can print",
            param="shaft_diameter",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} must sit under shaft_diameter {shaft_diameter}",
            param="shaft_across_flat",
        )
    if shaft_across_flat < 2.0:
        reject(
            f"shaft_across_flat {shaft_across_flat} is under 2mm: raise it",
            param="shaft_across_flat",
        )
    if knob_width < 28.0:
        reject(
            f"knob_width {knob_width} is under 28mm: wet hands need that much to grab",
            param="knob_width",
        )
    if knob_length < knob_width * 1.12:
        reject(
            f"knob_length {knob_length} must reach 12% past knob_width {knob_width}",
            param="knob_length",
        )
    if knob_height < 12.0:
        reject(
            f"knob_height {knob_height} is under 12mm: the stem stands 12mm proud",
            param="knob_height",
        )

    # Extra on the opening: past the 0.3mm virtual stem, under the 1.0mm rattle stem.
    clearance = 0.5
    bore_r = (shaft_diameter + clearance) / 2.0
    bore_across = shaft_across_flat + clearance
    # Flat faces +X; distance from the round's -X crown to the flat is bore_across.
    flat_x = -bore_r + bore_across

    body = extrude(SlotOverall(knob_length, knob_width), amount=knob_height)

    d_profile = Circle(bore_r) - Pos(flat_x, 0) * Rectangle(
        bore_r * 2.0,
        bore_r * 4.0,
        align=(Align.MIN, Align.CENTER),
    )
    cutter = Pos(0, 0, -1) * extrude(d_profile, amount=knob_height + 2.0)
    body = body - cutter

    if draft:
        return body

    top = body.bounding_box().max.Z
    keep = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 1e-3
        and abs(e.bounding_box().max.Z - top) < 1e-3
    )
    return polish(body, keep, 1.0)
