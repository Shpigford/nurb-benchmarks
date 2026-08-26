from nurb import *


@part
def bundle_holder(
    bundle_diameter: float = 8.0,
    holder_length: float = 12.0,
    bundle_clearance: float = 0.4,
    back_thickness: float = 3.0,
    floor_thickness: float = 2.0,
    lip_thickness: float = 2.4,
    screw_hole_width: float = 4.4,
    draft: bool = False,
):
    """A wall clip that cradles a horizontal cable bundle on one M4 screw.

    bundle_diameter: how thick the cable bundle is where it passes through
    holder_length: how far the clip runs along the bundle
    bundle_clearance: slack added around the bundle so it drops in
    back_thickness: how much material the screw pulls through against the wall
    floor_thickness: how thick the shelf the bundle rests on is
    lip_thickness: how thick the outer wall that keeps the bundle from pulling off is
    screw_hole_width: the through-bore for the M4 screw shank
    """
    if bundle_diameter <= 0.0:
        reject("the bundle has to have a width", "bundle_diameter")
    if holder_length < 10.0:
        reject("the clip needs at least 10mm along the bundle to hold it", "holder_length")

    pocket = bundle_diameter + bundle_clearance
    head_radius = 4.2          # M4 pan head plus driver
    slack = 0.2                # so the bundle is not pinched against the lip
    L = holder_length

    pocket_x0 = back_thickness
    lip_x0 = pocket_x0 + pocket + slack
    width = lip_x0 + lip_thickness

    lip_height = 0.70 * pocket
    screw_z = floor_thickness + pocket + head_radius + 0.4
    back_height = screw_z + head_radius + 0.8

    def slab(x0, x1, z0, z1):
        return Pos(x0, 0.0, z0) * Box(
            x1 - x0, L, z1 - z0,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        )

    body = slab(0.0, width, 0.0, floor_thickness)                       # shelf, on the bed
    body += slab(0.0, back_thickness, 0.0, back_height)                 # wall plate
    body += slab(lip_x0, width, 0.0, floor_thickness + lip_height)      # retaining lip

    bore = Pos(-1.0, 0.0, screw_z) * Rot(0.0, 90.0, 0.0) * Cylinder(
        screw_hole_width / 2.0, back_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body -= bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = {e for e in concave_edges(body)}
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e not in concave
        and e.geom_type == GeomType.LINE
    )
    return polish(body, keep, 1.2)
