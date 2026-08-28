from nurb import *


@part
def bit_block(
    shank_diameter=measured("shank_diameter"),
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall_thickness=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """A bench block that stands driver bits upright in a grid of round pockets.

    shank_diameter: how wide the bit shanks measure across
    columns: how many pockets along the long side of the block
    rows: how many pockets along the short side of the block
    pocket_clearance: how much wider a pocket is than the shank, so bits drop straight in
    pocket_depth: how far a bit sinks into the block
    wall_thickness: material between neighbouring pockets, and from the outer pockets to the sides
    floor_thickness: solid material under the pocket floors
    chamfer_size: the 45 degree lead-in on the pocket mouths and the break on the top rim
    """
    if columns < 1 or rows < 1:
        reject("a block needs at least one pocket", param="columns")
    if pocket_clearance < 0.1:
        reject(
            f"pocket_clearance {pocket_clearance} binds on the shank: a printed bore "
            f"comes out under size, so keep it at 0.1 or more (0.3 is the drop-in fit)",
            param="pocket_clearance",
        )
    if chamfer_size < 0.8:
        reject(
            f"a {chamfer_size}mm chamfer is under the 0.8mm floor and prints as a "
            f"defect rather than a lead-in: raise it to 0.8 or more",
            param="chamfer_size",
        )
    if 2 * chamfer_size >= wall_thickness:
        # Measured: at 8.3 pitch a 1.0 chamfer lands none of the ten mouths, because
        # OCCT needs more than 2 x chamfer of flat between two chamfered edges and the
        # land between neighbouring mouths is exactly `wall_thickness`. Refusing beats
        # `polish` quietly handing back a block with no lead-ins at all.
        reject(
            f"a {chamfer_size}mm chamfer leaves no flat between neighbouring pocket "
            f"mouths on {wall_thickness}mm walls, so the lead-ins will not land: keep "
            f"chamfer_size under {wall_thickness / 2:.2f}, or widen wall_thickness "
            f"past {2 * chamfer_size:.2f}",
            param="chamfer_size",
        )

    pocket_diameter = shank_diameter + pocket_clearance
    if pocket_diameter < 2.0:
        reject(
            f"a {pocket_diameter:.2f}mm pocket is under the 2mm floor for a printed "
            f"bore and would close up: raise shank_diameter above "
            f"{2.0 - pocket_clearance:.2f}",
            param="shank_diameter",
        )

    # One pitch is a pocket plus one wall, so `wall_thickness` is the material both
    # between neighbours and out to the sides. Everything else follows from it.
    pitch = pocket_diameter + wall_thickness
    width = (columns - 1) * pitch + pocket_diameter + 2 * wall_thickness
    depth = (rows - 1) * pitch + pocket_diameter + 2 * wall_thickness
    height = floor_thickness + pocket_depth

    body = Pos(0, 0, height / 2) * Box(width, depth, height)

    # Flat-floored bores opening straight up: self-supporting, nothing roofing them.
    bore = Pos(0, 0, height - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)
    for i in range(columns):
        for j in range(rows):
            x = (i - (columns - 1) / 2) * pitch
            y = (j - (rows - 1) / 2) * pitch
            body -= Pos(x, y) * bore

    if draft:
        return body

    # Only the top: every pocket mouth plus the top outer perimeter. The bottom
    # perimeter and the vertical corners stay sharp, so the block sits flat and the
    # bounding box is exactly width x depth x height.
    rim = body.edges().filter_by(lambda e: e.bounding_box().min.Z > height - 1e-6)
    return polish(body, rim, chamfer_size)
