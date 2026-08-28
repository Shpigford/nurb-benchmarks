from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    outside_width=30.0,
    knob_height=15.0,
    bore_depth=12.5,
    bore_clearance=0.7,
    draft=False,
):
    """A compact square replacement knob for an upright D-shaped valve stem.

    shaft_diameter: diameter across the round side of the valve stem.
    shaft_across_flat: distance from the D-flat to the opposite round side.
    outside_width: width across the knob's straight grip faces.
    knob_height: overall printed height from the bed to the top face.
    bore_depth: depth of the blind stem socket, measured down from the top.
    bore_clearance: total dimensional clearance added to each stem measurement.
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if not shaft_diameter / 2.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must lie between half the shaft diameter and the full shaft diameter",
            param="shaft_across_flat",
        )
    if bore_clearance <= 0.3:
        reject(
            "bore_clearance must exceed 0.3mm so the specified fit envelope can enter",
            param="bore_clearance",
        )
    if bore_clearance >= 1.0:
        reject(
            "bore_clearance must stay below 1.0mm so the knob does not rattle on the stem",
            param="bore_clearance",
        )
    if knob_height < bore_depth + 2.0:
        reject(
            "knob_height must leave at least 2mm of material under the blind bore",
            param="knob_height",
        )

    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    if outside_width < bore_diameter + 5.0:
        reject(
            "outside_width must leave at least 2.5mm around the bore",
            param="outside_width",
        )

    # The D bore is the round stem envelope clipped at its +X-facing flat. It opens
    # upward, so the 2.5mm floor remains grounded while the socket prints support-free.
    raw_body = Box(outside_width, outside_width, knob_height)
    if draft:
        body = raw_body
    else:
        bed = raw_body.bounding_box().min.Z
        top_outer_edges = raw_body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > bed
        )
        body = polish(raw_body, top_outer_edges, 1.0)

    bore_radius = bore_diameter / 2.0
    bore_center_z = knob_height / 2.0 - bore_depth / 2.0
    round_bore = Cylinder(bore_radius, bore_depth).translate((0.0, 0.0, bore_center_z))
    flat_x = -bore_radius + bore_across_flat
    clip_width = bore_diameter * 2.0
    flat_side = Box(clip_width, clip_width, bore_depth).translate(
        (flat_x - clip_width / 2.0, 0.0, bore_center_z)
    )
    # Cut after polishing so the fit-critical bore mouth remains sharp and exact.
    return body - (round_bore & flat_side)
