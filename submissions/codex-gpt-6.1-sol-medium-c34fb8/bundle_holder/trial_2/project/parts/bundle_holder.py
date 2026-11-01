"""Support-free wall mounting eye for a horizontal cable bundle."""
from math import sqrt
from nurb import *


@part
def bundle_holder(bundle_diameter=8.0, draft=False):
    """A closed cable passage beneath an accessible M4 screw.

    bundle_diameter: measured width of the cable bundle, with 0.4 mm extra clearance.
    """
    if bundle_diameter < 4.0:
        reject("bundle_diameter must be at least 4 mm", param="bundle_diameter")
    radius = (bundle_diameter + 0.4) / 2.0
    length = 10.8
    back_thickness = 2.8
    center_x = 3.0 + radius
    center_z = 2.0 + radius
    roof_top = center_z + sqrt(2.0) * radius + 2.9
    screw_height = roof_top + 4.5
    height = screw_height + 5.0
    front = center_x + radius + 2.0
    # This outline is extruded along Y. The roof's undersides are 45 degrees.
    outline = Polygon(
        (0, 0), (front, 0),
        (front, roof_top - (front - center_x)),
        (center_x, roof_top),
        (back_thickness, roof_top - (center_x - back_thickness)),
        (back_thickness, height), (0, height), align=None,
    )
    body = extrude(Plane.XZ * outline, amount=length / 2.0, both=True)
    # A circle with its upper 90-degree sector replaced by two tangent chords.
    tangent = radius / sqrt(2.0)
    roof = Polygon(
        (center_x - tangent, center_z + tangent),
        (center_x, center_z + sqrt(2.0) * radius),
        (center_x + tangent, center_z + tangent), align=None,
    )
    passage = Pos(center_x, 0, center_z) * extrude(
        Plane.XZ * Circle(radius), amount=length, both=True
    )
    passage += extrude(Plane.XZ * roof, amount=length, both=True)
    body -= passage
    # The screw shank passes through the back. Its head seats at X=2.8,
    # above the entire cable eye, leaving an unobstructed driver approach.
    screw_radius = 2.2
    screw_tangent = screw_radius / sqrt(2.0)
    screw_circle = Pos(0, 0, screw_height) * extrude(
        Plane.YZ * Circle(screw_radius), amount=back_thickness + 1, both=True
    )
    screw_roof = Plane.YZ * Polygon(
        (-screw_tangent, screw_height + screw_tangent),
        (0, screw_height + sqrt(2.0) * screw_radius),
        (screw_tangent, screw_height + screw_tangent), align=None,
    )
    body -= screw_circle + extrude(screw_roof, amount=back_thickness + 1, both=True)
    if draft:
        return body
    # Only the outer roof crest and mounting tab's exposed upper edge:
    # preserve the wall contact, the bore, and the cable fit surfaces.
    exposed = body.edges().filter_by(lambda edge:
        edge.bounding_box().size.Y > length - 0.01
        and edge.bounding_box().size.X < 0.01
        and edge.bounding_box().size.Z < 0.01
        and ((abs(edge.center().X - center_x) < 0.01
              and abs(edge.center().Z - roof_top) < 0.01)
             or (abs(edge.center().X - back_thickness) < 0.01
                 and abs(edge.center().Z - height) < 0.01)))
    return polish(body, exposed, 1.0)
