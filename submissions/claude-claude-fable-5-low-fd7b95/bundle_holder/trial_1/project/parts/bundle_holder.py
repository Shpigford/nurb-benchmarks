from nurb import *

# measured: bundle_diameter, calipers across the taped cable bundle (measurements.toml)


@part
def bundle_holder(
    bundle_diameter=8.0,
    holder_length=10.0,
    back_thickness=2.6,
    floor_thickness=2.0,
    lip_thickness=1.6,
    clearance=0.4,
    draft=False,
):
    """A wall hook for a horizontal cable bundle, one M4 screw.

    bundle_diameter: how thick the cable bundle is across
    holder_length: how far the holder runs along the bundle
    back_thickness: how thick the plate against the wall is
    floor_thickness: how thick the shelf under the bundle is
    lip_thickness: how thick the front lip is
    clearance: extra room in the channel so the bundle slides in
    """
    if bundle_diameter < 2.0:
        reject(
            "bundle_diameter under 2mm leaves no printable channel: raise it",
            param="bundle_diameter",
        )

    d = bundle_diameter
    c = clearance
    t = back_thickness
    ch = d + c  # channel opening, wall face to lip face

    floor_top = floor_thickness
    bundle_z = floor_top + 0.2 + d / 2.0  # bundle rests just above the floor
    lip_x = t + ch  # inner face of the front lip
    lip_top = bundle_z + 1.2
    outer_x = lip_x + lip_thickness

    head_r = 4.2  # M4 pan head + driver envelope, radius
    screw_z = floor_top + 0.2 + d + head_r + 0.2  # head clears the bundle
    top_z = screw_z + 4.0  # a bore diameter of plate above the axis

    # One cross-section in XZ, extruded along the bundle: back plate,
    # floor under the bundle, lip in front of it.
    profile = Polyline(
        (0, 0),
        (outer_x, 0),
        (outer_x, lip_top),
        (lip_x, lip_top),
        (lip_x, floor_top),
        (t, floor_top),
        (t, top_z),
        (0, top_z),
        close=True,
    )
    body = extrude(make_face(Plane.XZ * profile), -holder_length)

    # M4 clearance bore through the back plate, axis along X (into the wall).
    bore = Cylinder(2.2, t + 4.0, rotation=(0, 90, 0)).move(
        Location((t / 2.0, holder_length / 2.0, screw_z))
    )
    body = body - bore

    if draft:
        return body

    eps = 1e-6
    concave = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > eps  # nothing lying in the bed face
        and e.bounding_box().max.X > eps  # nothing lying in the wall face
        # the channel is fit geometry: no lead-in chamfers inside it
        and not (e.bounding_box().min.X > t - eps and e.bounding_box().max.X < lip_x + eps)
        and e not in concave
    )
    return polish(body, keep, 1.0)
