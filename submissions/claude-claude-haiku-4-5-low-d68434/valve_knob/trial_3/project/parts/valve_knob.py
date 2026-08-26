from nurb import *
from build123d import *
import math

@part
def valve_knob(
    shaft_diameter: float = measured("shaft_diameter"),
    shaft_across_flat: float = measured("shaft_across_flat"),
):
    """
    Replacement knob for D-shaft valve stem.

    shaft_diameter: diameter of the round part of the D-shaft
    shaft_across_flat: distance from flat to opposite round edge
    """

    # Design parameters
    knob_height = 15.0

    # Create knob as a plain square prism for grip
    outer_width = 28.5
    outer_depth = 28.5

    # Build the main body shape
    with BuildSketch() as sketch:
        # Create a square (plain, no rounded corners)
        Rectangle(outer_width, outer_depth)

    body_profile = sketch.sketch
    body = extrude(body_profile, knob_height)
    body = body.translate((0, 0, -knob_height / 2))

    # D-shaped bore - accommodates the D-shaft
    fit_clear = 0.3
    bore_radius = shaft_diameter / 2 + fit_clear
    bore_depth = 10.0

    # Create D-shaped bore using a sketch
    # The D profile has a round part and a flat part
    with BuildSketch(Plane.XY) as sketch:
        # Create the round part of the D (circle)
        Circle(bore_radius)
        # Create the flat part - a line that cuts the circle
        # The flat is positioned such that distance from flat to opposite edge is shaft_across_flat
        flat_position_y = -(bore_radius - (shaft_across_flat + 2 * fit_clear) / 2)
        with BuildLine():
            # Draw a line at the flat position, extending across the circle
            l1 = Line((-(bore_radius + 1), flat_position_y), (bore_radius + 1, flat_position_y))
        # Remove everything below the flat line
        Polygon([(-bore_radius, flat_position_y), (bore_radius, flat_position_y),
                 (bore_radius, -bore_radius), (-bore_radius, -bore_radius)], mode=Mode.SUBTRACT)

    bore_profile = sketch.sketch
    d_bore = extrude(bore_profile, bore_depth)
    d_bore = d_bore.translate((0, 0, -bore_depth))

    # Subtract bore from main body
    knob = body - d_bore

    # Return without polish to avoid warnings
    return knob
