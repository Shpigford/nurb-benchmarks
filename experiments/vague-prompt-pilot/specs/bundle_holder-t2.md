# Build spec: parts/bundle_holder.py — wall-mount cable bundle holder

## 1. Concept and form

1. The part is a "J" channel. A flat back plate mounts to the wall. A floor arm extends out from the bottom. A vertical lip rises at the outer edge. The bundle drops into the open-top slot between the back plate and the lip. Gravity plus the lip keep it in place.
2. One M4 pan-head screw holds the part to the wall, above the slot. The bundle load hangs straight below the screw, so one screw is enough. Do not add a second hole.
3. Overall envelope at the current measurement: 15.4 mm (X) × 12 mm (Y) × 24 mm (Z). Keep it this small. No ribs, no fillets, no decoration.

## 2. Coordinate frame and print orientation

4. Wall plane = X = 0. The back face is flat, full height, with no protrusions. +X points away from the wall.
5. The bundle axis is Y. The part is a constant profile in X–Z, extruded 12 mm in Y (Y = 0 to 12).
6. Down is −Z. The bed is the Z = 0 plane; the part prints standing in mounted orientation. The floor arm and the back-plate bottom edge form the bed footprint (about 15.4 × 12 mm). All other faces are vertical or slope ≤ 45°, so there are no supports and no bridges.

## 3. Parameters

7. `d` = `bundle_diameter` from measurements.toml (currently 8.0). Read it from the file; never hard-code 8.0.
8. `c` = 0.4 (radial slide-fit clearance for a printed slot around a soft taped bundle). A literal constant is fine.
9. Every dimension in section 4 marked with a formula must be computed from `d` in code, so a re-measure regenerates a correct part.

## 4. Profile geometry (X–Z, all values mm)

10. Back plate: X = 0 to 4, Z = 0 to 24. Formula: top Z = floor + (d + c) + 12.6 → round is not required; use `3 + (d + c) + 12.6`.
11. Floor arm: Z = 0 to 3, X = 0 to lip outer face (15.4). Formula: outer X = 4 + (d + c) + 3.
12. Slot (channel): X = 4 to 4 + (d + c) = 12.4 wide, open at the top, full Y width. The bundle rests on the floor at Z = 3; bundle top sits at Z = 3 + d = 11.
13. Lip: X = 12.4 to 15.4 (3 mm thick), Z = 3 up to 3 + 0.75·d = 9. The lip top must be above the bundle centerline (Z = 7); 0.75·d guarantees this. Keep the lip inner face vertical — no inward curl.
14. Lead-in chamfers: 1.5 mm × 45° on the top inner edge of the lip and on the back-plate inner face at the slot mouth (edge at Z = 24, X = 4). These guide the bundle as the user slides it down the wall into the slot.

## 5. Screw interface (M4 pan head)

15. One through-hole, axis along X, through the back plate (X = 0 to 4).
16. Hole Ø 4.5 mm (M4 clearance, printed-hole allowance included). Plain cylinder; no countersink and no counterbore — a pan head seats on the flat outer face of the back plate.
17. Hole center: Y = 6 (mid-width), Z = 3 + (d + c) + 6.6 = 18. This puts the head bottom (head Ø ≈ 8) 2.6 mm above the bundle top, and leaves 6 mm of plate above the hole center.
18. Driver access check: at Z = 18 the path from +X to the hole is clear — the lip stops at Z = 9. Do not add any geometry above Z = 9 outboard of X = 4.

## 6. Constraints for the implementation

19. Back-plate thickness 4 mm, floor 3 mm, lip 3 mm, width 12 mm — fixed constants, do not thicken.
20. No fillets, no supports-dependent features, no overhangs steeper than 45°. Every face is on the bed, vertical, or a 45° chamfer.
21. Solid part, no shelling. At this size, slicer infill keeps plastic use low; the model stays a plain solid.
22. Output file: `parts/bundle_holder.py`. The slot width, lip height, floor outer reach, back-plate height, and screw-hole Z must all be expressions of `d` per the formulas above.