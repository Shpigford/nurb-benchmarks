Build spec below. The one design decision worth flagging: I used a radius-matched circular cradle (not a V-groove) because the soft finish forbids line/edge contact, and I put the arc center 0.25 mm above the pole center so the pole, resting in the slightly oversized groove, lands at exactly 18.0 mm.

# Build spec: pole_rest — parts/pole_rest.py

## 1. Purpose and form

1. The part is a small bench rest for a drying pole. It is one solid block with an upward-opening cradle groove. The pole drops in from above and lies across the rest.
2. Overall size: about 26.5 mm wide (X), 20.0 mm long (Y), 22.0 mm tall (Z). Exact values come from the formulas in section 4.

## 2. Coordinate frame and print orientation

3. The pole axis runs along Y. The bed is the bench. Down is −Z.
4. The base of the block is flat at Z = 0 and sits on the bed. Print the part in this orientation. Do not rotate it for printing.
5. Center the block on the origin in X and Y.

## 3. Parameters

6. `pole_diameter` = value from `measurements.toml` (currently 20.0). Read it from the file. Do not hardcode 20.0 anywhere.
7. Named constants inside the part file:
   - `CENTER_HEIGHT = 18.0` — pole center height above the bench. This is a fixture constant that matches the other rests in the row. It does not come from measurements.toml.
   - `CLEARANCE = 0.25` — radial clearance for an FDM drop-in fit (0.5 mm on diameter).
   - `WALL = 3.0` — side wall thickness.
   - `LENGTH = 20.0` — block length along Y.
8. Every dimension in section 4 must be a formula of these values, so a new `pole_diameter` produces a correct part with the pole center still at 18.0 mm.

## 4. Cradle geometry (the critical numbers)

9. Cradle radius: `R_c = pole_diameter/2 + CLEARANCE` = 10.25.
10. Cradle arc center: X = 0, Z = `CENTER_HEIGHT + CLEARANCE` = 18.25. **Do not** put the arc center at 18.0. The pole (radius 10.0) rests on the bottom of the oversized groove, so its center sits `CLEARANCE` below the arc center. With the arc center at 18.25, the pole center lands at exactly 18.0. The groove bottom is at Z = 8.0, so 8.0 mm of solid material sits under the pole.
11. Groove shape: a full circular arc of radius `R_c` from the bottom up to the equator (the widest point, at Z = 18.25). Above the equator, the groove walls are vertical planes at X = ±`R_c`, up to the top of the block. This gives a constant opening of `2 × R_c` = 20.5 mm, so the 20.0 mm pole drops straight in. Never narrow the opening above the equator.
12. The cradle surface must be a true circular arc (radius match), not a V-groove and not a chamfered notch. Edge or point contact will mark the soft finish.
13. The groove runs the full length of the block along Y (open at both Y ends).

## 5. Block envelope

14. Width (X): `2 × R_c + 2 × WALL` = 26.5.
15. Length (Y): `LENGTH` = 20.0.
16. Height (Z): `CENTER_HEIGHT + 4.0` = 22.0. This leaves 4 mm of wall above the pole center to keep the pole captured.
17. Lead-in: chamfer the two top inner edges of the groove opening at 45°, 2.0 mm, so the opening flares from 20.5 mm to 24.5 mm at the very top. This guides the drop-in.

## 6. Print economy and support check

18. No supports are needed: every surface is flat on the bed, vertical, upward-facing (the groove), or a 45° upward flare (the lead-in). Verify none of your operations creates a downward-facing overhang.
19. Keep the part exactly this: one block minus one groove minus two chamfers. No ribs, no hollowing, no fillets on outer edges, no base flanges. The slicer's infill handles material savings; small footprint handles the rest.
20. Do not extend `LENGTH` beyond 20.0. The row of rests supplies stability along the pole; each rest only needs enough footprint not to tip, and 26.5 × 20.0 at 22.0 tall with the pole's weight pressing down is sufficient.

## 7. Acceptance checks (assert or verify these in the model)

21. Lowest point of the groove is at Z = `CENTER_HEIGHT - pole_diameter/2 + CLEARANCE` (8.0 by wait — verify: 18.25 − 10.25 = 8.0). A 20.0 mm cylinder seated in the groove has its center at Z = 18.0 ± 0.01.
22. Minimum opening width anywhere above Z = 18.25 is ≥ `pole_diameter + 2 × CLEARANCE` (20.5).
23. The base at Z = 0 is a single flat rectangle, 26.5 × 20.0.
24. Groove is symmetric about the X = 0 plane; a seated pole is centered over the rest.