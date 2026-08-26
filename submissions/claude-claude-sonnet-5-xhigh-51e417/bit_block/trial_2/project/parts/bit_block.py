from nurb import *


@part
def bit_block(
    shank_diameter=6.0,
    columns=5,
    rows=2,
    pocket_clearance=0.3,
    pocket_depth=12.0,
    wall_between=2.0,
    edge_margin=2.0,
    floor_thickness=3.0,
    chamfer_size=0.8,
    draft=False,
):
    """Bench block holding driver bits upright in a grid of round pockets.

    shank_diameter: the bit shank's diameter, across the widest point
    columns: how many pockets sit side by side, left to right
    rows: how many pockets sit front to back
    pocket_clearance: extra room in each pocket over the bare shank
    pocket_depth: how far down each pocket reaches
    wall_between: material left between neighbouring pocket walls
    edge_margin: material left from the outermost pocket wall to the block's side
    floor_thickness: solid material under the pockets
    chamfer_size: the lead-in chamfer on every pocket mouth and the top perimeter
    """
    if columns < 1 or rows < 1:
        reject("bit_block needs at least one column and one row of pockets", param="columns")

    pocket_dia = shank_diameter + pocket_clearance
    if pocket_dia < 2.0:
        reject(
            f"shank_diameter {shank_diameter} gives a {pocket_dia:.2f}mm pocket, under the "
            "2mm minimum hole size: raise shank_diameter",
            param="shank_diameter",
        )

    pitch = pocket_dia + wall_between
    height = floor_thickness + pocket_depth

    grid_span_x = (columns - 1) * pitch
    grid_span_y = (rows - 1) * pitch
    length = grid_span_x + pocket_dia + 2 * edge_margin
    width = grid_span_y + pocket_dia + 2 * edge_margin

    block = Box(length, width, height)

    top_z = height / 2
    pocket_center_z = top_z - pocket_depth / 2
    for i in range(columns):
        x = -grid_span_x / 2 + i * pitch
        for j in range(rows):
            y = -grid_span_y / 2 + j * pitch
            pocket = Pos(x, y, pocket_center_z) * Cylinder(pocket_dia / 2, pocket_depth)
            block -= pocket

    if draft:
        return block

    concave = concave_edges(block)
    lead_in = block.edges().filter_by(
        lambda e: e not in concave
        and abs(e.bounding_box().min.Z - top_z) < 1e-6
        and abs(e.bounding_box().max.Z - top_z) < 1e-6
    )
    return polish(block, lead_in, chamfer_size)
