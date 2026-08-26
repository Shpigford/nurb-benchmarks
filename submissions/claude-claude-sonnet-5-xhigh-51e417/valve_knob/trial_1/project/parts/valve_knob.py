from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    grip_width=28.4,
    knob_height=15.5,
    cap_thickness=3.0,
    bore_clearance=0.6,
    draft=False,
):
    """
    shaft_diameter: how wide the valve stem is straight across
    shaft_across_flat: how wide the stem measures from its flat face to the round side opposite it
    grip_width: how wide the knob measures across its flats, for a wet-hand grip
    knob_height: how tall the finished knob stands
    cap_thickness: how much solid material sits above the bore, under the grip's outer face
    bore_clearance: how much roomier the bore is than the bare stem, split across its round side and its flat side
    """
    shaft_radius = shaft_diameter / 2.0
    shaft_flat_depth = shaft_across_flat - shaft_radius
    if not (0.0 < shaft_flat_depth < shaft_radius):
        reject(
            f"shaft_across_flat {shaft_across_flat} has to sit between the shaft "
            f"radius ({shaft_radius}) and its full diameter ({shaft_diameter}) to "
            "describe a real D-flat",
            param="shaft_across_flat",
        )

    bore_radius = shaft_radius + bore_clearance / 2.0
    bore_flat_depth = shaft_flat_depth + bore_clearance / 2.0

    apothem = grip_width / 2.0
    if bore_radius + 2.0 >= apothem:
        reject(
            f"grip_width {grip_width} is too narrow to wrap this shaft: widen it "
            f"past {2 * (bore_radius + 2.0):.1f}",
            param="grip_width",
        )

    bore_depth = knob_height - cap_thickness
    if bore_depth <= 0.0:
        reject(
            f"cap_thickness {cap_thickness} leaves no room for the bore under "
            f"knob_height {knob_height}",
            param="cap_thickness",
        )
    stem_proud_height = measured("stem_proud_height")
    if bore_depth < stem_proud_height:
        reject(
            f"bore_depth {bore_depth:.1f} (knob_height minus cap_thickness) is "
            f"shallower than the {stem_proud_height}mm the stem stands proud: the "
            "knob would perch on the tip instead of seating",
            param="knob_height",
        )

    # A square: its corner-to-corner reach is sqrt(2) (~41%) past its face-to-face
    # width, which is what gives a wet hand real purchase, with room to spare once
    # the corners below are chamfered back. Faces already land facing +/-X and
    # +/-Y, so the bore's flat below simply lines up with one of them.
    body = extrude(Rectangle(grip_width, grip_width), knob_height)

    # The D-shaped bore: a circle with its +X segment sliced off by a flat at
    # x = bore_flat_depth, so the stem's flat (also facing +X) locks rotation.
    clip_margin = bore_radius + 5.0
    clip_width = bore_flat_depth + clip_margin
    clip = Pos((bore_flat_depth - clip_margin) / 2.0, 0) * Rectangle(clip_width, 2 * clip_margin)
    bore_profile = Circle(bore_radius) & clip

    top = body.bounding_box().max.Z
    bore = Pos(0, 0, top) * extrude(bore_profile, -bore_depth)
    body -= bore

    if draft:
        return body

    # Polish the vertical corners only: the edges a gripping hand actually meets.
    # Chamfering the top rim too would land a third facet on each of these same
    # corners and leave slivers under a square millimetre. The bore's own two
    # vertical seams are concave (mating geometry besides), so they drop out here
    # without needing a separate exclusion.
    concave = concave_edges(body)

    def is_vertical_corner(edge):
        bbox = edge.bounding_box()
        return bbox.max.X - bbox.min.X < 1e-6 and bbox.max.Y - bbox.min.Y < 1e-6

    keep = body.edges().filter_by(is_vertical_corner).filter_by(lambda e: e not in concave)
    return polish(body, keep, 1.0)
