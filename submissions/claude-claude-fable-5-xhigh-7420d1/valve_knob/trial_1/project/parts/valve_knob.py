from nurb import *
import math


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    stem_height=12.0,
    bore_clearance=0.6,
    knob_width=30.0,
    corner_radius=7.0,
    floor_thickness=3.0,
    draft=False,
):
    """Replacement knob for a valve with a D-shaped stem. Prints bore-up and flips onto the stem.

    shaft_diameter: the stem's full round diameter, measured with calipers
    shaft_across_flat: from the stem's flat to its round side
    stem_height: how far the stem stands proud of the valve body
    bore_clearance: extra room in the bore over the stem, in total (a printed bore comes out small)
    knob_width: the knob across its flats, the narrowest you can measure it
    corner_radius: how rounded the four corners are; smaller is squarer and reaches further
    floor_thickness: material between the end of the bore and the face you see in use
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}, so the stem has no flat and the knob could not turn it",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter / 2:
        reject(
            f"shaft_across_flat {shaft_across_flat} is under half the diameter: the flat "
            f"would cut past the stem's centre. Re-measure; it should be over {shaft_diameter / 2}",
            param="shaft_across_flat",
        )
    if bore_clearance < 0.2:
        reject(
            f"bore_clearance {bore_clearance} is a bind that varies by machine: use 0.2 or more",
            param="bore_clearance",
        )
    if floor_thickness < 2.0:
        reject(
            f"floor_thickness {floor_thickness} is under the 2mm minimum wall",
            param="floor_thickness",
        )
    if corner_radius < 0 or corner_radius >= knob_width / 2:
        reject(
            f"corner_radius {corner_radius} must sit between 0 and half of knob_width "
            f"({knob_width / 2})",
            param="corner_radius",
        )

    # The bore is the stem grown by the clearance: the diameter and the across-flat each
    # gain the whole clearance, so the flat sits half of it further out than the stem's.
    bore_dia = shaft_diameter + bore_clearance
    bore_r = bore_dia / 2
    flat_x = (shaft_across_flat + bore_clearance) - bore_r
    bore_depth = stem_height + 0.5  # the knob seats on the valve body, not on the stem tip
    height = bore_depth + floor_thickness

    if knob_width / 2 - bore_r < 3.0:
        reject(
            f"knob_width {knob_width} leaves under 3mm of wall beside the bore: raise it "
            f"above {2 * (bore_r + 3.0):.1f}",
            param="knob_width",
        )

    # Four flats for wet hands, corners blended so there is no vertical edge anywhere:
    # the rim chamfer then runs as one band and leaves no corner slivers.
    if corner_radius > 0:
        outline = RectangleRounded(knob_width, knob_width, corner_radius)
    else:
        outline = Rectangle(knob_width, knob_width)
    body = extrude(outline, height)

    # D-bore: a circle with its +X side cut flat, opening up through the top face.
    bore_profile = Circle(bore_r) - Pos(flat_x + bore_r, 0) * Rectangle(2 * bore_r, 2 * bore_r + 2)
    bore = Pos(0, 0, floor_thickness) * extrude(bore_profile, bore_depth + 1.0)
    body = body - bore

    if draft:
        return body

    # Polish the top rim only: the bed face stays flat and the bore mouth stays sharp,
    # because a mating mouth takes no lead-in.
    top = body.bounding_box().max.Z
    rim = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-3
        and math.hypot(e.center().X, e.center().Y) > bore_r + 1.0
    )
    concave = set(concave_edges(body))
    rim = [e for e in rim if e not in concave]
    return polish(body, rim, 1.0)
