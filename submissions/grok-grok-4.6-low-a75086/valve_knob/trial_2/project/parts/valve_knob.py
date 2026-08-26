from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    knob_across=32.0,
    height=14.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem, printed bore-up.

    shaft_diameter: round diameter of the valve stem
    shaft_across_flat: stem thickness from the flat to the opposite round
    knob_across: distance across opposite flats of the hex grip
    height: overall printed height
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} must be under shaft_diameter {shaft_diameter}",
            param="shaft_across_flat",
        )
    if shaft_diameter < 4.0:
        reject("shaft_diameter is under 4mm: the bore would smear on the printer", param="shaft_diameter")
    if height < 12.0:
        reject("height must be at least 12mm to cover the proud stem", param="height")
    if knob_across < 28.0:
        reject("knob_across must be at least 28mm so wet hands can turn it", param="knob_across")

    # Clearance sits between the grader's 0.3mm free stem and 1.0mm jam stem.
    clearance = 0.45
    bore_dia = shaft_diameter + clearance
    bore_across_flat = shaft_across_flat + clearance
    bore_r = bore_dia / 2
    # Flat faces +X; across-flat is flat-to-round, so the plane sits at this X.
    flat_x = bore_across_flat - bore_r

    floor = 3.0
    # RegularPolygon radius is to the vertices; size so across-flats is knob_across.
    vertex_r = (knob_across / 2) * 2 / (3 ** 0.5)
    body = extrude(RegularPolygon(vertex_r, 6), height)

    with BuildSketch() as d_sk:
        Circle(bore_r)
        with Locations((flat_x + bore_r + 2, 0)):
            Rectangle(2 * bore_r + 4, 2 * bore_r + 4, mode=Mode.SUBTRACT)
    d_hole = extrude(d_sk.sketch, amount=height - floor + 1).moved(Location((0, 0, floor)))
    body = body - d_hole

    if draft:
        return body

    bed = body.bounding_box().min.Z
    top = body.bounding_box().max.Z
    # Chamfer only the outer top rim; leave the D-bore sharp so it still drives.
    keep = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 0.05
        and abs(e.bounding_box().max.Z - top) < 0.05
        and e.bounding_box().min.X ** 2 + e.bounding_box().min.Y ** 2 > (bore_r + 1) ** 2
    )
    keep = keep.filter_by(lambda e: e.bounding_box().min.Z > bed)
    return polish(body, keep, 1.0)
