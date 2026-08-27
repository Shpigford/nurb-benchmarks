from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    draft=False,
):
    """Hold a horizontal cable bundle against a wall with one M4 screw.

    bundle_diameter: measured width across the cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            "bundle_diameter below 4 mm leaves too little room for the M4 mounting layout",
            param="bundle_diameter",
        )

    length = 12.0
    wall_thickness = 2.6
    cradle_thickness = 2.4
    fit_clearance = 0.6
    channel_width = bundle_diameter + fit_clearance

    cable_center_z = cradle_thickness + channel_width / 2
    lip_height = cable_center_z + 0.3 * bundle_diameter
    screw_center_z = cradle_thickness + channel_width + 6.0
    plate_height = screw_center_z + 5.4
    total_depth = wall_thickness + channel_width + cradle_thickness

    back = Box(
        wall_thickness,
        length,
        plate_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        total_depth,
        length,
        cradle_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    retaining_lip = Box(
        cradle_thickness,
        length,
        lip_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness + channel_width, 0, 0))

    holder = back + floor + retaining_lip

    screw_bore = (
        Cylinder(
            2.2,
            wall_thickness + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        .rotate(Axis.Y, 90)
        .translate((-0.1, length / 2, screw_center_z))
    )
    holder = holder - screw_bore

    if draft:
        return holder

    exposed_outer_edges = holder.edges().filter_by(Axis.Y).filter_by(
        lambda edge: (
            abs(edge.center().X - wall_thickness) < 0.01
            and abs(edge.center().Z - plate_height) < 0.01
        )
        or (
            abs(edge.center().X - total_depth) < 0.01
            and abs(edge.center().Z - lip_height) < 0.01
        )
    )
    return polish(holder, exposed_outer_edges, 1.0)
