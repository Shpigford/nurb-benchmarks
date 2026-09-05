# Build spec — parts/bundle_holder.py

## 1. Overview

1. The part is a wall-mounted cable-bundle clip: a flat back plate against the wall, a mounting foot with one M4 hole at the bottom, and an open-top hook cradle above it. The bundle drops into the cradle from above, sliding down along the wall, and a lip snaps it in.
2. Bounding box: 15 mm deep (X) × 10 mm wide (Y) × 33 mm tall (Z). Volume ≈ 2.5 cm³.
3. One solid body. Constant cross-section in X–Z, extruded 10.0 mm along Y (Y = 0 to 10). Only the screw hole breaks the extrusion.

## 2. Frame and print orientation

4. Wall = plane X = 0. Back face of the part lies flat in that plane, with no features except the screw hole exit.
5. Bundle axis = Y. Down = −Z. Bed = plane Z = 0. Print exactly as modeled; do not rotate.
6. The bed-contact face is the bottom of the foot: X 0→6, Y 0→10, at Z = 0.

## 3. Body: outer profile (X, Z), extruded Y 0→10

7. Closed polygon, counterclockwise: (0, 0) → (6, 0) → (6, 12) → (15, 21) → (15, 30) → (3, 30) → (0, 33) → close to (0, 0).
8. Meaning of each segment: bottom face on bed; foot front face (screw-head seat); 45° underside chamfer (the support-free underside of the cradle); front wall; top face; 45° entry ramp on the plate top, which guides a bundle sliding down the wall out and into the slot; back face on the wall.

## 4. Cuts (A–D extruded through full Y width; overshoot every cut ≥1 mm past outer faces)

9. Cut A — channel: lower half-disc, center (7.5, 24.0), radius 4.5 (bore Ø9.0), the half with Z ≤ 24. This is the saddle the bundle rests in.
10. Cut B — entry slot: box X 3.0→9.0, Z 24.0 → above the top. Slot width 6.0 mm. Back wall of the slot is the plate front face (X = 3); front wall is the lip inner face (X = 9).
11. Cut C — lip underside chamfer: triangle (9, 24), (12, 24), (9, 27). This gives the lip a 45° underside so it prints without support, and opens the channel front-top so the bundle can compress past the lip.
12. Cut D — mouth lead-in: triangle (9, 30), (9, 28), (11, 30). Funnels the bundle into the slot.
13. Cut E — screw hole: cylinder Ø4.5, axis along X, center at Y = 5.0, Z = 6.0, through the foot (X 0→6).

## 5. Screw interface (one M4 pan-head)

14. One screw only. Hole Ø4.5 = M4 clearance (4.3 nominal + 0.2 printed-hole compensation). Do not thread it.
15. Head seat = foot front face at X = 6, spanning Z 0→12. Pan head Ø8.0 × 3.1 tall seats flat: head spans Z 2→10 and Y 1→9, inside the face. Head top (Z = 10) clears the chamfer overhead (Z = 12 at X = 6) by 2 mm; driver access along +X is open air.
16. No counterbore, no countersink.

## 6. Bundle interface (drives retention — get these exact)

17. Channel bore = bundle_diameter + 1.0 = 9.0 mm. Slip fit: the bundle slides along Y and seats by gravity.
18. Slot gap = 0.75 × bundle_diameter = 6.0 mm. The soft bundle compresses 25% to pass the lip, then springs back. This is the "stays put" mechanism; do not widen it.
19. Lip tip at (9, 27) overhangs the seated bundle's cross-section by ~0.4 mm — that overlap plus the 6.0 gap is the retention. Lip inner face X = 9 is vertical from Z = 27 to 28 (then Cut D chamfer).

## 7. measurements.toml → parameters

20. Read `bundle_diameter` (D = 8.0) from measurements.toml. Never hard-code 8.0.
21. Derive from D (keep these as formulas in code): channel radius r = (D + 1.0)/2; channel center Xc = 3 + r; slot gap = 0.75 × D; slot back at X = 3, slot front at X = 3 + gap; lip slant from (Xc + r, Zc) to (3 + gap, Zc + (Xc + r − 3 − gap)); part top = lip-tip Z + 3.
22. Channel center height: Zc = 24.0 for D = 8. If D changes, set Zc so the perpendicular distance from (Xc, Zc) to the chamfer line Z = X + 6 is ≥ r + 2.5.
23. Fixed constants (name them, but do not derive from D): wall thickness 3.0, width 10.0, foot depth 6.0, foot height 12.0, screw hole Ø4.5, screw hole center Z = 6.0.

## 8. Keep it minimal / support-free rules

24. No fillets. The only chamfers are the four already specified (underside, ramp, Cuts C and D).
25. Every downward-facing surface is on the bed, vertical, or exactly 45°. Do not add any feature that breaks this. The Ø4.5 horizontal hole is the only bridge; leave it round.
26. Width stays 10 mm; add no ribs, no second screw hole, no logo, no extra body.

## 9. Acceptance checks before you finish

27. Back face is flat at X = 0 with only the Ø4.5 hole in it.
28. Section at Y = 5 matches the profile and cuts above; slot gap measures 6.0; bore measures 9.0.
29. Bottom face at Z = 0 measures 6 × 10. Nothing extends below Z = 0 or behind X = 0.
30. Slicing in mounted orientation reports zero support material.