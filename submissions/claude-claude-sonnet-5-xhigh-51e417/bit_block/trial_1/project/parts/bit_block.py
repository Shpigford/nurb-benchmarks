from nurb import *


@part
def bit_block(shank_diameter=measured("shank_diameter"), columns=5, draft=False):
    """A bench block of round pockets that hold driver bits upright by their shanks.

    shank_diameter: the bits' shank diameter, which sets each pocket's bore
    columns: how many pockets sit side by side in a row
    """
    if columns < 1:
        reject(f"columns {columns} must be at least 1", param="columns")

    pocket_dia = shank_diameter + 0.3
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} gives a {pocket_dia:.2f}mm pocket, "
            "under the 2mm printable hole minimum: raise shank_diameter",
            param="shank_diameter",
        )

    rows = 2
    pocket_depth = 12.0
    wall_between = 2.0
    edge_margin = 2.0
    floor_thickness = 3.0
    chamfer_size = 0.8

    pitch = pocket_dia + wall_between
    width = columns * pocket_dia + (columns - 1) * wall_between + 2 * edge_margin
    depth = rows * pocket_dia + (rows - 1) * wall_between + 2 * edge_margin
    height = floor_thickness + pocket_depth

    block = Box(width, depth, height)
    top_z = block.bounding_box().max.Z

    pocket_r = pocket_dia / 2
    pocket_tool = Cylinder(
        pocket_r, pocket_depth + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    x_start = -pitch * (columns - 1) / 2
    y_start = -pitch * (rows - 1) / 2
    pockets = [
        Pos(x_start + i * pitch, y_start + j * pitch, top_z - pocket_depth) * pocket_tool
        for i in range(columns)
        for j in range(rows)
    ]

    tool = pockets[0]
    for p in pockets[1:]:
        tool = tool + p
    body = block - tool

    if draft:
        return body

    top_face = lambda e: (
        abs(e.bounding_box().min.Z - top_z) < 1e-6
        and abs(e.bounding_box().max.Z - top_z) < 1e-6
    )
    rim_edges = body.edges().filter_by(GeomType.CIRCLE).filter_by(top_face)
    perimeter_edges = body.edges().filter_by(GeomType.LINE).filter_by(top_face)

    return polish(body, rim_edges + perimeter_edges, chamfer_size)
