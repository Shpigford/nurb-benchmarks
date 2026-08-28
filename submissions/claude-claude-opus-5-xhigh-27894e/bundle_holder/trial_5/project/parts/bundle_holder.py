from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.8,
    holder_length=12.4,
    wall_thickness=2.4,
    back_thickness=3.0,
    lip_rise=2.0,
    screw_hole_width=4.4,
    screw_head_width=8.4,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that carries a horizontal cable bundle on one M4 screw.

    bundle_diameter: how thick the cable bundle is across
    bundle_clearance: extra room around the bundle so it drops into the cradle
    holder_length: how far the holder runs along the bundle
    wall_thickness: how thick the cradle floor and the front lip are
    back_thickness: how much material the screw pulls through against the wall
    lip_rise: how far the front lip stands above the middle of the bundle
    screw_hole_width: the through-hole for the M4 wall screw
    screw_head_width: room the screw head and driver need in front of the back plate
    chamfer_size: the chamfer taken off every exposed edge
    """
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves the bundle no room to thread"
            " through: raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if wall_thickness < 1.6:
        reject(
            f"wall_thickness {wall_thickness} is under two perimeters of floor and lip:"
            " raise it to 1.6 or more",
            param="wall_thickness",
        )
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} gives the screw less than 2.4 of material"
            " to pull through: raise it to 2.4 or more",
            param="back_thickness",
        )
    if screw_hole_width < 4.2:
        reject(
            f"screw_hole_width {screw_hole_width} will not clear an M4 shank once the"
            " bore prints under size: raise it to 4.2 or more",
            param="screw_hole_width",
        )
    if holder_length < screw_head_width + 1.0:
        reject(
            f"holder_length {holder_length} leaves no plate around the screw head for it"
            f" to bear on: raise it above {screw_head_width + 1.0}",
            param="holder_length",
        )
    if lip_rise < 1.2:
        reject(
            f"lip_rise {lip_rise} does not reach far enough over the bundle to stop it"
            " rolling out: raise it to 1.2 or more",
            param="lip_rise",
        )

    groove_r = (bundle_diameter + bundle_clearance) / 2
    x_axis = back_thickness + groove_r          # channel centre, out from the wall
    z_axis = wall_thickness + groove_r          # channel centre, up from the bed
    x_front = x_axis + groove_r + wall_thickness
    cradle_top = z_axis + lip_rise
    bundle_top = z_axis + bundle_diameter / 2
    bore_r = screw_hole_width / 2
    head_r = screw_head_width / 2

    # The screw sits high enough that its head and the driver reaching it both pass
    # clear over the cradle and over the bundle lying in it.
    screw_z = max(cradle_top, bundle_top) + head_r + 0.4
    # and the plate carries a full head's worth of material around the bore at the seat,
    # with the top chamfer taken off above that.
    height = screw_z + head_r + chamfer_size + 0.4

    profile = Plane.XZ * (
        Rectangle(x_front, cradle_top, align=(Align.MIN, Align.MIN))
        + Rectangle(back_thickness, height, align=(Align.MIN, Align.MIN))
        - Pos(x_axis, z_axis) * Circle(groove_r)
        - Pos(x_axis, z_axis) * Rectangle(2 * groove_r, lip_rise, align=(Align.CENTER, Align.MIN))
    )
    body = extrude(profile, amount=holder_length / 2, both=True)
    body -= (
        Pos(back_thickness / 2, 0, screw_z)
        * Rot(0, 90, 0)
        * Cylinder(bore_r, back_thickness + 2)
    )

    if draft:
        return body

    def stamp(edge):
        b = edge.bounding_box()
        return tuple(
            round(v, 3)
            for v in (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)
        )

    concave = {stamp(e) for e in concave_edges(body)}
    eps = 0.05

    def on_channel(p):
        """True where a point sits on the wall of the run the bundle threads through.

        A curved edge's bounding box comes back inflated, so the channel is tested by
        sampling the edge itself: the end arcs read as ordinary exposed edges otherwise
        and pick up a lead-in chamfer the doctrine retires.
        """
        radial = ((p.X - x_axis) ** 2 + (p.Z - z_axis) ** 2) ** 0.5
        if radial < groove_r + 0.1 and p.Z < cradle_top + 0.1:
            return True
        return abs(p.X - x_axis) < groove_r + 0.1 and z_axis - 0.1 < p.Z < cradle_top + 0.1

    def on_seam(p):
        """True at the line where the groove runs tangent into the back plate's face.

        A chamfer started on an edge that ends here does not stop here: the kernel
        carries it around the tangent arc and takes a full chamfer out of the floor
        under the bundle, which is most of the floor. The plate's front corners stay
        sharp instead, and the card says so.
        """
        radial = ((p.X - x_axis) ** 2 + (p.Z - z_axis) ** 2) ** 0.5
        return abs(radial - groove_r) < 0.05 and p.Z < cradle_top + 0.1

    def exposed(edge):
        b = edge.bounding_box()
        if stamp(edge) in concave:
            return False
        if b.max.X < eps:                       # lies in the back face, against the wall
            return False
        if b.max.Z < eps:                       # lies in the bed face
            return False
        if all(on_channel(edge @ t) for t in (0.25, 0.5, 0.75)):
            return False                        # the run the bundle threads through
        if any(on_seam(edge @ t) for t in (0.0, 1.0)):
            return False                        # tangent into the run: see on_seam
        if (                                    # the bore and the seat the head bears on
            b.max.X < back_thickness + eps
            and b.min.Y > -bore_r - eps
            and b.max.Y < bore_r + eps
            and b.min.Z > screw_z - bore_r - eps
            and b.max.Z < screw_z + bore_r + eps
        ):
            return False
        return True

    return polish(body, body.edges().filter_by(exposed), chamfer_size)
