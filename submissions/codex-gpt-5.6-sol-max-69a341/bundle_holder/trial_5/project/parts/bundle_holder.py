from math import sqrt

from nurb import *


def _teardrop_profile(center_x, center_z, radius):
    """A circular clearance with a printable 45 degree roof."""
    tangent = radius / sqrt(2.0)
    circle = Pos(center_x, center_z) * Circle(radius)
    roof = Polygon(
        (center_x - tangent, center_z + tangent),
        (center_x + tangent, center_z + tangent),
        (center_x, center_z + radius * sqrt(2.0)),
    )
    return circle + roof


def _support_free_outer_profile(center_x, center_z, radius):
    """A flat-bottomed envelope with vertical sides and a 45 degree roof."""
    shoulder_z = center_z + radius * (sqrt(2.0) - 1.0)
    peak_z = center_z + radius * sqrt(2.0)
    return Polygon(
        (center_x - radius, center_z - radius),
        (center_x + radius, center_z - radius),
        (center_x + radius, shoulder_z),
        (center_x, peak_z),
        (center_x - radius, shoulder_z),
    )


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Hold a horizontal cable bundle against a wall with one M4 screw.

    bundle_diameter: measured width across the cable bundle
    """
    if bundle_diameter < 2.0:
        reject(
            "bundle_diameter under 2mm leaves no useful cable passage; raise it to at least 2mm",
            param="bundle_diameter",
        )

    length = 10.0
    bundle_clearance = 0.4
    shell = 2.1

    # The screw bears on the front of this plate. Its 2.5mm thickness exceeds
    # the required 2.4mm shank length before the head seat.
    wall_plate_thickness = 2.5
    screw_hole_radius = 4.4 / 2.0
    screw_head_radius = 8.4 / 2.0
    screw_head_height = 3.2

    cable_radius = bundle_diameter / 2.0 + bundle_clearance / 2.0
    outer_radius = cable_radius + shell
    cable_center_z = shell + cable_radius

    # A full wall-width gap separates the plate and tunnel above the connecting
    # floor. It also keeps the installed screw head well behind the cable.
    plate_to_tunnel_gap = max(
        shell, screw_head_height + bundle_clearance / 2.0 - shell
    )
    cable_center_x = (
        wall_plate_thickness + plate_to_tunnel_gap + outer_radius
    )

    outer_profile = _support_free_outer_profile(
        cable_center_x, cable_center_z, outer_radius
    )
    inner_profile = _teardrop_profile(
        cable_center_x, cable_center_z, cable_radius
    )
    outer_tunnel = extrude(
        Plane.XZ * outer_profile, amount=length / 2.0, both=True
    )
    tunnel_clearance = extrude(
        Plane.XZ * inner_profile, amount=length / 2.0 + 0.1, both=True
    )
    tunnel = outer_tunnel - tunnel_clearance

    outer_peak_z = cable_center_z + outer_radius * sqrt(2.0)
    screw_center_z = outer_peak_z + screw_head_radius + 0.4
    plate_height = screw_center_z + screw_head_radius + 1.0
    tunnel_front_x = cable_center_x + outer_radius

    plate = Box(
        wall_plate_thickness,
        length,
        plate_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    floor = Box(
        tunnel_front_x,
        length,
        shell,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    # A teardrop bore contains the full 4.4mm circular clearance while replacing
    # only the unsupported top arc with two printable 45 degree roof faces.
    bore_profile = _teardrop_profile(0.0, screw_center_z, screw_hole_radius)
    bore_plane = Plane.YZ.offset(wall_plate_thickness / 2.0)
    bore = extrude(
        bore_plane * bore_profile,
        amount=wall_plate_thickness / 2.0 + 0.2,
        both=True,
    )

    body = plate + floor + tunnel
    body = body - bore

    if draft:
        return body

    # Polish only the exposed outer roof ridge. The wall face, bed face, cable
    # passage, and screw seat remain dimensionally exact.
    ridge = body.edges().filter_by(
        lambda edge: abs(edge.bounding_box().min.Z - outer_peak_z) < 0.01
        and abs(edge.bounding_box().max.Z - outer_peak_z) < 0.01
        and edge.length > length - 0.01
    )
    return polish(body, ridge, 1.0)
