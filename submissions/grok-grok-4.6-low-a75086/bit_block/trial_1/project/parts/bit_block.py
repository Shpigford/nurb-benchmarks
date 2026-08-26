from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    draft=False,
):
    """Bench block that holds driver bits upright in a grid of round pockets.

    shank_diameter: measured width of a bit shank
    columns: number of pockets along the long side
    """
    pocket_clearance = 0.3
    pocket_depth = 12.0
    floor_thickness = 3.0
    wall = 2.0
    lead_in = 0.8
    rows = 2

    if columns < 1:
        reject("columns must be at least 1 so a bit has a pocket", param="columns")
    if shank_diameter < 2.0:
        reject(
            "shank_diameter is under 2mm; a printed pocket that small will close",
            param="shank_diameter",
        )

    pocket_dia = shank_diameter + pocket_clearance
    pitch = pocket_dia + wall
    height = pocket_depth + floor_thickness
    margin = pocket_dia / 2 + wall
    width = (columns - 1) * pitch + 2 * margin
    depth = (rows - 1) * pitch + 2 * margin

    with BuildPart() as bp:
        Box(width, depth, height)
        top = bp.faces().sort_by(Axis.Z)[-1]
        with Locations(top):
            with GridLocations(pitch, pitch, columns, rows):
                Hole(pocket_dia / 2, depth=pocket_depth)
        if not draft:
            top_z = bp.part.bounding_box().max.Z
            mouths = bp.edges().filter_by(GeomType.CIRCLE).filter_by(
                lambda e: abs(e.center().Z - top_z) < 1e-4
            )
            outer_top = (
                bp.edges()
                .filter_by(GeomType.LINE)
                .filter_by(
                    lambda e: abs(e.bounding_box().min.Z - top_z) < 1e-4
                    and abs(e.bounding_box().max.Z - top_z) < 1e-4
                )
            )
            chamfer(mouths + outer_top, lead_in)

    return bp.part
