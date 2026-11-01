"""Wall-mounted cable channel, printed in its mounted orientation."""
from nurb import *
from math import sqrt


@part
def bundle_holder(bundle_diameter=float(measured("bundle_diameter")), draft=False):
    """Hold a horizontal cable bundle with a single accessible M4 screw.

    bundle_diameter: measured width of the cable bundle; changes the channel width and lip height
    """
    if bundle_diameter < 4.0:
        reject("bundle_diameter must be at least 4 mm", param="bundle_diameter")
    length = 12.0
    back_thickness = 3.0
    floor_thickness = 2.4
    lip_thickness = 2.4
    channel_width = bundle_diameter + 0.4
    cable_center_height = floor_thickness + channel_width / 2
    lip_height = cable_center_height + 1.4
    screw_height = cable_center_height + bundle_diameter / 2 + 6.0
    back_height = screw_height + 6.0
    width = back_thickness + channel_width + lip_thickness

    body = Box(width, length, floor_thickness, align=(Align.MIN, Align.CENTER, Align.MIN))
    body += Box(back_thickness, length, back_height, align=(Align.MIN, Align.CENTER, Align.MIN))
    body += Pos(back_thickness + channel_width, 0, 0) * Box(
        lip_thickness, length, lip_height, align=(Align.MIN, Align.CENTER, Align.MIN))

    # Circle plus a tangent 45-degree roof: the entire 4.4 mm bore stays clear.
    bore_radius = 2.2
    roof_contact = bore_radius / sqrt(2)
    bore_plane = Plane(origin=(-0.1, 0, screw_height), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    roof_profile = Polygon(
        (-roof_contact, roof_contact), (roof_contact, roof_contact),
        (0, bore_radius * sqrt(2)), align=None)
    bore = extrude(bore_plane * Circle(bore_radius), amount=back_thickness + 0.2)
    roof = extrude(bore_plane * roof_profile, amount=back_thickness + 0.2, dir=(1, 0, 0))
    body = body - bore - roof

    if draft:
        return body
    # Only the long top lip edges: leave the wall datum, bore and seat untouched.
    lip_edges = body.edges().filter_by(lambda e:
        abs(e.center().Z - lip_height) < 0.01
        and e.length > length - 0.01)
    return polish(body, lip_edges, 1.0)
