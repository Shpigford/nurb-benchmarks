from nurb import *


@part
def bundle_holder(bundle_diameter: float = measured("bundle_diameter"), draft=False):
    """Wall-mounted cable cradle with a separate, accessible M4 screw seat.

    bundle_diameter: measured width of the cable bundle; the channel adds 0.4 mm.
    """
    if bundle_diameter < 4.0:
        reject("Use a bundle_diameter of at least 4 mm", param="bundle_diameter")

    length = 12.0
    back_thickness = 3.0
    wall_thickness = 2.4
    channel_width = bundle_diameter + 0.4
    front_inside = back_thickness + channel_width
    outside = front_inside + wall_thickness
    lip_height = wall_thickness + channel_width
    # The complete 8.4 mm driver envelope clears the lip by 2 mm.
    screw_height = lip_height + 6.2
    back_height = screw_height + 6.2

    # One constant cross-section along Y: nothing obstructs the cable's run.
    outline = Plane.XZ * Polygon(
        (0, 0), (outside, 0), (outside, lip_height),
        (front_inside, lip_height), (front_inside, wall_thickness),
        (back_thickness, wall_thickness), (back_thickness, back_height),
        (0, back_height), align=None,
    )
    body = extrude(outline, amount=length / 2, both=True)
    screw = Pos(back_thickness / 2, 0, screw_height) * Cylinder(
        radius=2.2, height=back_thickness + 2.0, rotation=(0, 90, 0)
    )
    body = body - screw
    if draft:
        return body

    # Dress the two exposed long top edges; preserve the back, screw seat,
    # channel dimensions, bed perimeter and full-thickness end cross-sections.
    top_edges = body.edges().filter_by(
        lambda e: e.geom_type == GeomType.LINE
        and abs(e.length - length) < 1e-5
        and (
            (abs(e.center().X - outside) < 1e-5
             and abs(e.center().Z - lip_height) < 1e-5)
            or (abs(e.center().X - back_thickness) < 1e-5
                and abs(e.center().Z - back_height) < 1e-5)
        )
    )
    return polish(body, top_edges, 1.0)
