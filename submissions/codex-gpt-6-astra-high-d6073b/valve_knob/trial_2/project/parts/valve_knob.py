from nurb import *


@part
def valve_knob(
    shaft_diameter=float(measured("shaft_diameter")),
    shaft_across_flat=float(measured("shaft_across_flat")),
    grip_length=40.0,
    grip_width=28.4,
    knob_height=14.0,
    bore_depth=11.0,
    shaft_clearance=0.5,
    draft=False,
):
    """Oval valve knob, printed with its blind D socket facing upward.

    shaft_diameter: measured diameter of the stem's round portion.
    shaft_across_flat: measured distance from the flat to the opposite round side.
    grip_length: overall length of the oval hand grip.
    grip_width: narrowest width of the oval hand grip.
    knob_height: total height above the flat print bed.
    bore_depth: depth of stem engagement measured down from the open top.
    shaft_clearance: extra clearance on the diameter and across-flat dimension.
    """
    if not shaft_diameter / 2 < shaft_across_flat < shaft_diameter:
        reject("The flat distance must be between half and all of the shaft diameter.",
               param="shaft_across_flat")
    if shaft_clearance <= 0:
        reject("Shaft clearance must be positive.", param="shaft_clearance")
    if bore_depth <= 0 or knob_height - bore_depth < 3.0:
        reject("Leave at least 3 mm of closed floor beneath the bore.", param="bore_depth")
    if grip_length < grip_width:
        reject("Grip length must be at least the grip width.", param="grip_length")
    bore_radius = (shaft_diameter + shaft_clearance) / 2
    if grip_width < 2 * bore_radius + 8.0:
        reject("Leave at least 4 mm of material around the bore.", param="grip_width")

    body = extrude(SlotOverall(grip_length, grip_width), amount=knob_height)

    # The +X flat is measured from the circle's -X extremity, not its axis.
    flat_x = shaft_across_flat + shaft_clearance - bore_radius
    floor_z = knob_height - bore_depth
    cutter_height = bore_depth + 1.0
    round_bore = Pos(0, 0, floor_z) * Cylinder(
        bore_radius, cutter_height, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    flat_limit = Pos(flat_x, 0, floor_z) * Box(
        2 * bore_radius + 1.0, 2 * bore_radius + 2.0, cutter_height,
        align=(Align.MAX, Align.CENTER, Align.MIN),
    )
    body = body - (round_bore & flat_limit)

    if draft:
        return body
    # Soften the exposed outer rim; preserve the bed and every mating edge.
    rim = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > knob_height - 0.001
        and max(abs(edge.center().X), abs(edge.center().Y)) > bore_radius + 1.0
    )
    return polish(body, rim, 1.0)
