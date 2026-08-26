from nurb import *
import math


def teardrop(radius, along_y, x, z):
    """A round bore roofed by two 45 degree chords, cut along Y: prints without support."""
    apex = radius * math.sqrt(2)
    profile = Circle(radius) + Polygon((-radius, 0), (radius, 0), (0, apex), align=None)
    solid = extrude(profile, along_y).rotate(Axis.X, 90)  # apex to +Z, run along -Y
    return solid.moved(Location((x, along_y, z)))


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    length=10.0,
    wall=2.0,
    bundle_clearance=0.6,
    plate_thickness=2.6,
    screw_hole_width=4.4,
    draft=False,
):
    """
    bundle_diameter: how thick the cable bundle is
    length: how long the holder runs along the bundle
    wall: material around the bundle tunnel
    bundle_clearance: extra room in the tunnel so the bundle threads through
    plate_thickness: thickness of the back plate the screw goes through
    screw_hole_width: the screw's clearance hole (M4 medium fit)
    """
    r = (bundle_diameter + bundle_clearance) / 2
    if r < 1.0:
        reject("bundle_diameter is too small to make a tunnel", param="bundle_diameter")
    apex = r * math.sqrt(2)
    # Tunnel block: back at x=0, bed at z=0.
    block_w = plate_thickness + 2 * r + wall
    block_h = wall + apex + wall
    zc = wall + r
    xc = plate_thickness + r
    block = Box(block_w, length, block_h, align=(Align.MIN, Align.MIN, Align.MIN))

    # Screw plate rising above the tunnel, bore along X.
    plate_h = 2 * screw_hole_width + 2.4
    plate = Box(plate_thickness, length, plate_h, align=(Align.MIN, Align.MIN, Align.MIN))
    plate = plate.moved(Location((0, 0, block_h)))
    zs = block_h + plate_h / 2
    body = block + plate

    body = body - teardrop(r, length, xc, zc)
    rb = screw_hole_width / 2
    bore_profile = Circle(rb) + Polygon((0, -rb), (0, rb), (rb * math.sqrt(2), 0), align=None)
    bore = extrude(bore_profile, plate_thickness + 2).rotate(Axis.Y, -90)  # run along -X, apex +Z
    bore = bore.moved(Location((plate_thickness + 1, length / 2, zs)))
    if draft:
        return body - bore
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.01)
    keep = keep.filter_by(lambda e: e not in concave_edges(body) and e.length > 4.0)
    # Polish first, then cut the screw bore, so its rim stays sharp and full-width.
    return polish(body, keep, 1.0) - bore
