from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_height=16.0,
    grip_radius=14.5,
    lobe_extension=4.5,
    bore_clearance=0.7,
):
    """Three-lobed replacement handle for an 8 mm D-shaft valve.

    shaft_diameter: diameter measured across the round portion of the valve stem
    shaft_across_flat: distance from the stem flat to its opposite round side
    knob_height: total printed height of the knob
    grip_radius: radius of the round core between the grip lobes
    lobe_extension: how far each of the three wet-hand grip lobes projects
    bore_clearance: extra modeled room across both D-shaft measurements
    """
    if shaft_diameter <= 0.0 or shaft_across_flat <= 0.0:
        reject("shaft dimensions must be positive", param="shaft_diameter")
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D-shaft",
            param="shaft_across_flat",
        )
    if knob_height < 15.0:
        reject("knob_height must leave a 3mm socket floor; use 15mm or more", param="knob_height")
    if grip_radius < 14.0:
        reject("grip_radius must be at least 14mm for a secure hand grip", param="grip_radius")
    if bore_clearance < 0.35 or bore_clearance >= 1.0:
        reject(
            "bore_clearance must stay from 0.35mm to under 1.0mm so the D-shaft both fits and drives",
            param="bore_clearance",
        )

    # A circular core and three low, rounded lobes keep every layer self-supporting.
    knob = Cylinder(grip_radius, knob_height)
    for angle in (0.0, 120.0, 240.0):
        theta = radians(angle)
        center = (
            grip_radius * cos(theta),
            grip_radius * sin(theta),
            0.0,
        )
        knob += Cylinder(lobe_extension, knob_height).move(Location(center))

    # The socket is a D: the flat is on +X.  Build a cylinder, then remove its +X cap.
    # It opens upward and stops on a 3 mm floor for the 12 mm proud valve stem.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_depth = knob_height - 3.0
    # Primitive cylinders are centered on Z, so locate the socket by its center.
    bore_center_z = (knob_height - bore_depth) / 2.0
    flat_x = bore_across_flat - bore_radius

    bore = Cylinder(bore_radius, bore_depth).move(Location((0.0, 0.0, bore_center_z)))
    cap = Box(
        bore_radius * 2.0,
        bore_radius * 2.0 + 2.0,
        bore_depth,
    ).move(Location((flat_x + bore_radius, 0.0, bore_center_z)))
    d_socket = bore - cap

    return knob - d_socket
