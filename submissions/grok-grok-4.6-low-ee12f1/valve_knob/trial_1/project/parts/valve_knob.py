from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    height=16.0,
    across=34.0,
    draft=False,
):
    """Replacement D-shaft valve knob, printed bore-up.

    shaft_diameter: round diameter of the valve stem
    shaft_across_flat: stem thickness from the flat to the round side
    height: how tall the knob prints
    across: distance across the hex flats, the narrowest grip
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be less than shaft_diameter for a D-stem",
            param="shaft_across_flat",
        )
    if height < 12.0:
        reject("height must be at least 12 so the stem can seat", param="height")
    if across < 28.0:
        reject("across must be at least 28 so wet hands can turn it", param="across")

    clearance = 0.5
    bore_dia = shaft_diameter + clearance
    bore_af = shaft_across_flat + clearance
    flat_x = bore_af - bore_dia / 2

    # Hex printed on the bed. Across-flats is the narrow grip; vertices give the 12% extra.
    body = extrude(RegularPolygon(across / 2, 6), height)

    stem = Cylinder(bore_dia / 2, height + 4)
    stem = stem.move(Location((0, 0, height / 2)))
    slab = Box(bore_dia + 4, bore_dia + 4, height + 6)
    slab = slab.move(Location((flat_x + (bore_dia + 4) / 2, 0, height / 2)))
    d_bore = stem - slab
    body = body - d_bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = keep - concave_edges(body)
    return polish(body, keep, 1.0)
