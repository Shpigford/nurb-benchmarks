from nurb import *

# Fixture requirement: pole center sits this high above the bench on the existing row.
center_height = 18.0


@part
def pole_rest(
    radial_clearance=0.25,
    wall=3.0,
    length_y=15.0,
    draft=False,
):
    """Drop-in rest that cradles a finishing pole on a circular groove.

    radial_clearance: extra radius so the wet pole drops in without scraping
    wall: solid beside the groove, each side
    length_y: how long the rest is along the pole
    """
    pole_diameter = measured("pole_diameter")
    groove_r = pole_diameter / 2 + radial_clearance
    # Floor stays at center_height − pole radius so clearance does not lift the pole.
    groove_floor = center_height - pole_diameter / 2
    height = groove_floor + groove_r
    width = pole_diameter + 2 * radial_clearance + 2 * wall

    body = Box(width, length_y, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    cutter = Cylinder(groove_r, length_y + 2)
    cutter = Location((0, 0, height), (90, 0, 0)) * cutter
    body = body - cutter

    if draft:
        return body

    mouth = body.edges().filter_by(Axis.Y).filter_by(
        lambda e: abs(e.center().Z - height) < 0.05 and abs(abs(e.center().X) - groove_r) < 0.05
    )
    return chamfer(mouth, 2.0)
