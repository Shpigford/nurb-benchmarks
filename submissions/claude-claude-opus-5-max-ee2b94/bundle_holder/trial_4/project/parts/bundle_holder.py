from nurb import *

# An M4 pan head is 8.0 across; 8.4 is that plus the slop a driver bit needs to
# reach the slot, and it is the diameter that has to stay clear from the seat out.
SCREW_HEAD_CLEARANCE = 8.4


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.6,
    holder_length=12.0,
    back_thickness=3.0,
    cradle_thickness=3.0,
    lip_height=6.0,
    screw_hole_width=4.4,
    screw_wall=3.0,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that carries a horizontal cable bundle on one M4 pan-head screw.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: extra room across the channel so the bundle drops in
    holder_length: how much of the bundle the holder grips, along the bundle
    back_thickness: the plate against the wall, and the length of the screw's grip
    cradle_thickness: how thick the shelf under the bundle and the front lip are
    lip_height: how far the front lip rises above the shelf
    screw_hole_width: clearance bore for the mounting screw, M4 medium fit
    screw_wall: plate left around the screw hole above it and to each side
    chamfer_size: the facet taken off every exposed edge
    """
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves the channel tighter than the "
            "0.4mm a printed channel needs to take its bundle: raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if bundle_clearance > 1.8:
        reject(
            f"bundle_clearance {bundle_clearance} lets the bundle drop most of a "
            "millimetre inside the channel before the shelf catches it, which is a "
            "rattle rather than a hold: bring it under 1.8",
            param="bundle_clearance",
        )
    if cradle_thickness < 1.6:
        reject(
            f"cradle_thickness {cradle_thickness} is under two printed beads, so the "
            "shelf and lip would flex aside instead of holding the bundle: raise it "
            "above 1.6",
            param="cradle_thickness",
        )
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} gives the screw less than the 2.4mm of "
            "grip its head needs to seat on: raise it above 2.4",
            param="back_thickness",
        )
    if lip_height < bundle_diameter * 0.4:
        reject(
            f"lip_height {lip_height} is under 40% of the {bundle_diameter}mm bundle, "
            "so the lip cannot catch it: raise it above "
            f"{round(bundle_diameter * 0.4, 1)}",
            param="lip_height",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed bore holds "
            "open: raise it above 2.0",
            param="screw_hole_width",
        )

    channel = bundle_diameter + bundle_clearance
    depth = back_thickness + channel + cradle_thickness
    lip_top = cradle_thickness + lip_height

    # The highest the bundle can sit and still be caught by the shelf below it: any
    # higher and it drops more than 1mm before touching. That worst case, not the
    # resting one, is what the screw head has to stay clear of.
    bundle_top = cradle_thickness + bundle_diameter + 1.0
    # The driver runs straight out over the open channel, so it clears whichever
    # stands taller: that worst-case bundle, or the lip itself.
    screw_z = max(bundle_top, lip_top) + SCREW_HEAD_CLEARANCE / 2 + 0.4

    # The head bears on the plate's front face, so the whole 8.4 washer circle has to
    # land on flat plate: the polish facet at the top and at each side stays outside it.
    bearing = SCREW_HEAD_CLEARANCE / 2 + chamfer_size + 0.4
    height = screw_z + max(screw_hole_width / 2 + screw_wall, bearing)
    least_length = max(screw_hole_width + 2 * screw_wall, 2 * bearing)
    if holder_length < least_length:
        reject(
            f"holder_length {holder_length} leaves too little plate beside the screw "
            f"for its head to bear on: raise it above {round(least_length, 1)}",
            param="holder_length",
        )

    corner = (Align.MIN, Align.CENTER, Align.MIN)
    back = Box(back_thickness, holder_length, height, align=corner)
    shelf = Box(depth, holder_length, cradle_thickness, align=corner)
    lip = Pos(depth - cradle_thickness) * Box(
        cradle_thickness, holder_length, lip_top, align=corner
    )
    body = back + shelf + lip

    # Axis along X, opening on the back face. Nothing stands in front of it at this
    # height, so the head seats on the plate's front face and the driver runs straight
    # out over the open channel: no counterbore, and no ceiling to bridge.
    bore = Pos(back_thickness / 2, 0.0, screw_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole_width / 2, back_thickness + 2.0
    )
    body = body - bore

    if draft:
        return body

    box = body.bounding_box()
    wall_face = box.min.X
    bed = box.min.Z
    concave = concave_edges(body)

    def sharp(edge):
        # The two bore rims are the screw's seat and its mouth at the wall: fit
        # geometry, never chamfered. Everything lying in the back or bottom face is
        # hidden against wall or bed, so a facet there buys nothing.
        if edge.geom_type == GeomType.CIRCLE:
            return True
        eb = edge.bounding_box()
        if eb.max.X < wall_face + 0.01 or eb.max.Z < bed + 0.01:
            return True
        return any(edge.is_same(c) for c in concave)

    keep = [e for e in body.edges() if not sharp(e)]
    return polish(body, keep, chamfer_size)
