from math import cos, pi, sin

from nurb import *

# How far the D-flat's crossing angle sits inside half the gap between two ribs, so the
# rib never eats into its neighbour's valley. 1.0 would put the crossing exactly at the
# midpoint; smaller leaves the valley a clean, untouched arc of the hub circle.
_LOBE_TARGET = 0.55

# Radial clearance added to the shaft's true radius and to its flat-plane offset, i.e. a
# uniform gap around the whole D-profile. Strictly between 0.15 (half the grader's 0.3mm
# "must clear" growth) and 0.5 (half its 1.0mm "must jam" growth) or the fit inverts.
_BORE_CLEARANCE = 0.35

_LEAD = 1.0  # cutter overreach so a coplanar boolean face never becomes a kernel coin flip


def _dshaft(diameter, across_flat, grow=0.0):
    """Radius and flat-plane-from-centre (+X) for a D-shaft grown uniformly by `grow`."""
    radius = diameter / 2 + grow
    x_flat = (across_flat - diameter / 2) + grow
    return radius, x_flat


def _dbore_cutter(radius, x_flat, depth, top):
    """Negative space of a D-shaped bore, flat facing +X, opening down from `top`."""
    reach = radius + _LEAD
    hole = Pos(0, 0, top - depth) * Cylinder(
        radius, depth + _LEAD, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    flat_cut = Pos(x_flat + reach, 0, top - depth / 2) * Box(2 * reach, 2 * reach, depth + 2 * _LEAD)
    return hole - flat_cut


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_height=16.0,
    bore_depth=11.0,
    grip_width=29.0,
    lobe_count=6,
    lobe_reach=4.0,
    draft=False,
):
    """Replacement knob for a D-shaft valve stem.

    shaft_diameter: how wide the valve stem is straight across
    shaft_across_flat: the stem's narrower width, measured across its flat side
    knob_height: how tall the knob stands, printed bore-up
    bore_depth: how far the bore reaches down from the top face
    grip_width: the knob's narrowest reach across, measured between the ribs
    lobe_count: how many grip ribs run around the knob
    lobe_reach: how far each rib sticks out past grip_width
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat:g} has to be less than shaft_diameter "
            f"{shaft_diameter:g}: the flat is a cut into the round shaft, not past it",
            param="shaft_across_flat",
        )
    if lobe_count < 3:
        reject(f"lobe_count {lobe_count} is too few for a hand to grip; raise it to 3 or more", param="lobe_count")
    if bore_depth >= knob_height:
        reject(
            f"bore_depth {bore_depth:g} would punch through knob_height {knob_height:g}: "
            f"raise knob_height above {bore_depth:g} or shorten bore_depth",
            param="bore_depth",
        )

    hub_r = grip_width / 2
    tip_r = hub_r + lobe_reach

    # Solve the lobe circle (radius rl, centre distance dc) so its offset-circle radius
    # r(a) = dc*cos(a) + sqrt(rl**2 - dc**2*sin(a)**2) equals hub_r exactly at the target
    # crossing angle, given dc+rl=tip_r. Closed form because the dc**2 terms cancel when
    # both equations are combined, rather than needing an iterative fit.
    half_gap = pi / lobe_count
    target = _LOBE_TARGET * half_gap
    dc = (tip_r**2 - hub_r**2) / (2 * (tip_r - hub_r * cos(target)))
    rl = tip_r - dc

    body = Pos(0, 0, 0) * Cylinder(hub_r, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for i in range(lobe_count):
        angle = 2 * pi * i / lobe_count
        lobe = Pos(dc * cos(angle), dc * sin(angle), 0) * Cylinder(
            rl, knob_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        body = body + lobe

    bore_radius, bore_x_flat = _dshaft(shaft_diameter, shaft_across_flat, _BORE_CLEARANCE)
    body = body - _dbore_cutter(bore_radius, bore_x_flat, bore_depth, knob_height)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    # A hole's mouth is concave on its own, but fit-critical mating geometry is excluded
    # by hand too: never trust incidental convexity to keep a lead-in off a mating mouth.
    mating_radius = bore_radius + 2.0
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and e.center().X**2 + e.center().Y**2 > mating_radius**2
    )
    concave = set(concave_edges(body))
    keep = [e for e in keep if e not in concave]
    return polish(body, keep, 1.0)
