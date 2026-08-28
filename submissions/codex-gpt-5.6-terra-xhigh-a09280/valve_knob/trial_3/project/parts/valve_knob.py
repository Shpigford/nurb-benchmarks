from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_height=15.0,
    hub_radius=14.5,
    wing_reach=35.0,
    wing_width=6.0,
    bore_clearance=0.8,
    base_thickness=2.0,
    draft=False,
):
    """A compact winged replacement knob for an 8 mm D-shaft valve stem.

    shaft_diameter: diameter across the stem's round section.
    shaft_across_flat: distance from the stem's flat to its opposite round side.
    knob_height: overall printed height from the bed to the top face.
    hub_radius: radius of the round hand grip around the shaft.
    wing_reach: farthest distance of either turning wing from the centerline.
    wing_width: front-to-back thickness of the turning wings.
    bore_clearance: added clearance on both D-shaft dimensions.
    base_thickness: solid floor retained below the upward-opening socket.
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be positive", param="shaft_diameter")
    if not 0.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be greater than 0 and smaller than shaft_diameter",
            param="shaft_across_flat",
        )
    if knob_height < base_thickness + 10.0:
        reject(
            "knob_height must leave a 10 mm-deep socket above base_thickness",
            param="knob_height",
        )
    if base_thickness < 2.0:
        reject("base_thickness must be at least 2 mm for a printable socket floor", param="base_thickness")
    if wing_reach <= hub_radius:
        reject("wing_reach must extend beyond hub_radius", param="wing_reach")

    # The circular hub guarantees a 29 mm minimum hand span.  The narrow wing pair
    # reaches 35 mm from center while keeping the print compact and material-efficient.
    hub = Cylinder(hub_radius, knob_height)
    wings = Box(wing_reach * 2.0, wing_width, knob_height)
    body = hub + wings

    # Socket faces upward while printing. The D-flat is at +X: the flat coordinate
    # is its distance from the opposite (-X) circular extreme.
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    bore_across_flat = shaft_across_flat + bore_clearance
    flat_x = bore_across_flat - bore_radius
    socket_depth = knob_height - base_thickness
    # Primitives are centered on Z, so this seats the socket floor exactly
    # base_thickness above the printed bottom face.
    round_socket = Cylinder(bore_radius, socket_depth).translate((0.0, 0.0, base_thickness / 2.0))
    remove_flat_side = Box(
        bore_radius + 2.0,
        bore_radius * 2.0 + 2.0,
        socket_depth,
    ).translate((flat_x + (bore_radius + 2.0) / 2.0, 0.0, base_thickness / 2.0))
    d_socket = round_socket - remove_flat_side
    finished = body - d_socket
    if draft:
        return finished

    # Soften only the four exposed vertical wing corners. The socket rim and every
    # bed-contact edge remain exact for fit and a full first layer.
    wing_tip_edges = finished.edges().filter_by(
        lambda edge: (
            edge.bounding_box().max.Z - edge.bounding_box().min.Z > knob_height - 0.01
            and abs((edge.bounding_box().min.X + edge.bounding_box().max.X) / 2.0) > wing_reach - 0.01
        )
    )
    return polish(finished, wing_tip_edges, 1.0)
