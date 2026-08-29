from math import cos, radians, sin

from nurb import *

BORE_CLEARANCE = 0.2
FLAT_CLEARANCE = 0.15
BORE_DEPTH = 12.5
KNOB_DIAMETER = 40.0
KNOB_HEIGHT = 18.0
CHAMFER = 1.0
SCALLOP_COUNT = 6
SCALLOP_DIAMETER = 12.0
SCALLOP_PITCH_RADIUS = 24.0


@part
def valve_knob(draft=False):
    """Replacement hose-valve knob for a D-shaft stem.

    Prints closed-face down, bore opening up. Shaft sizes come from
    measurements.toml; clearances are named constants.

    shaft_diameter / shaft_across_flat: stem sizes in measurements.toml.
    """
    shaft_diameter = measured("shaft_diameter")
    shaft_across_flat = measured("shaft_across_flat")
    bore_diameter = shaft_diameter + BORE_CLEARANCE
    flat_x = (shaft_across_flat - shaft_diameter / 2.0) + FLAT_CLEARANCE

    body = Cylinder(KNOB_DIAMETER / 2.0, KNOB_HEIGHT)
    body = Pos(0, 0, KNOB_HEIGHT / 2.0) * body

    for i in range(SCALLOP_COUNT):
        angle = i * (360.0 / SCALLOP_COUNT)
        sx = SCALLOP_PITCH_RADIUS * cos(radians(angle))
        sy = SCALLOP_PITCH_RADIUS * sin(radians(angle))
        scallop = Cylinder(SCALLOP_DIAMETER / 2.0, KNOB_HEIGHT + 2.0)
        body -= Pos(sx, sy, KNOB_HEIGHT / 2.0) * scallop

    floor_z = KNOB_HEIGHT - BORE_DEPTH
    bore = Cylinder(bore_diameter / 2.0, BORE_DEPTH + 2.0)
    bore = Pos(0, 0, floor_z + (BORE_DEPTH + 2.0) / 2.0) * bore
    # Keep the D void on the −X side of the flat; knob material stays +X of flat_x.
    clip = Box(80.0, 80.0, 80.0)
    clip = Pos(flat_x - 40.0, 0, KNOB_HEIGHT / 2.0) * clip
    body -= bore & clip

    if draft:
        return body

    opening = [
        e
        for e in body.edges()
        if abs(e.center().Z - KNOB_HEIGHT) < 0.05
        and (e.center().X ** 2 + e.center().Y ** 2) ** 0.5 < bore_diameter / 2.0 + 0.6
    ]
    if opening:
        body = chamfer(opening, CHAMFER)
    return body
