from nurb import *

# The bench fixes this: several rests stand in a row and the pole lies across
# them, axis along Y, always this high above the bed.
AXIS_HEIGHT = 18.0
# Radial air gap between the cradle and the pole surface (0.1-0.4mm window).
CLEARANCE = 0.25
# Radial material thickness behind the seat surface.
WALL = 3.5


@part
def pole_rest(pole_diameter=20.0, draft=False):
    """
    pole_diameter: how wide the pole is, straight across, at its finished diameter
    """
    radius = pole_diameter / 2.0
    seat_radius = radius + CLEARANCE
    floor_below = AXIS_HEIGHT - seat_radius
    if floor_below < 1.5:
        reject(
            f"pole_diameter {pole_diameter} puts the seat within {floor_below:.2f}mm "
            f"of the bed at the fixed {AXIS_HEIGHT}mm axis height; keep pole_diameter "
            f"under {2 * (AXIS_HEIGHT - CLEARANCE - 1.5):.1f} so the floor under the "
            "seat keeps its backing",
            param="pole_diameter",
        )

    half_width = seat_radius + WALL
    width = 2 * half_width
    length = max(24.0, 210.0 / width)

    block = Box(
        width, length, AXIS_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # A half-round channel, open at the top: full cylinder first, then trim
    # away everything above the pole's axis height so nothing overhangs the
    # drop-in path and the pole can only settle, never wedge.
    channel = Cylinder(
        seat_radius, length + 10.0,
        rotation=(90, 0, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    channel = Pos(0, 0, AXIS_HEIGHT) * channel

    upper_half = Box(
        seat_radius * 2 + 4.0, length + 20.0, seat_radius + 4.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    upper_half = Pos(0, 0, AXIS_HEIGHT) * upper_half

    seat_cut = channel - upper_half
    body = block - seat_cut

    if draft:
        return body

    # Name what must stay sharp: the bed-contact face, any concave edge, and
    # the seat itself (its rim and end arcs all sit exactly on the seat
    # cylinder, tangent to the shoulder, so the fold there reads convex to
    # `is_convex` even though it is mating geometry a lead-in chamfer would
    # ruin) are never polished. Let the kernel chamfer whatever else it can
    # take.
    def on_seat(edge):
        p = edge.center()
        d = ((p.X) ** 2 + (p.Z - AXIS_HEIGHT) ** 2) ** 0.5
        return abs(d - seat_radius) < 0.05

    concave = concave_edges(body)
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().max.Z > bed + 1e-6)
    keep = keep.filter_by(lambda e: e not in concave)
    keep = keep.filter_by(lambda e: not on_seat(e))
    # 1.2mm rather than the 1.0mm default: at 1.0mm the corner triangle three
    # chamfers leave at each outer corner (0.866 * size**2) lands just under
    # the 1mm2 sliver floor and fires a finding every build; 1.2mm clears it.
    return polish(body, keep, 1.2)
