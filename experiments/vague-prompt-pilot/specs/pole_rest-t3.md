Here is the build spec for `parts/pole_rest.py`. Hand it to the junior agent as-is.

---

## Build spec: pole_rest

**Purpose:** bench rest that cradles a wet-finish pole. Pole center must sit at exactly Z = 18.0 mm above the bench, centered over the rest. Pole drops in from above.

### 1. Parameters

1. `pole_d` = `pole_diameter` from measurements.toml (currently 20.0). This must stay parametric — read it from the file, never hardcode 20.0.
2. `center_height` = 18.0 (module constant; fixture-matching value, not in measurements.toml).
3. `fit_clearance` = 0.3 (module constant; radial clearance for a drop-in printed fit).
4. All derived dimensions below must be written as expressions of these three values.

### 2. Overall form

5. One solid rectangular block with an open-top U-slot cut through it along Y. No other features.
6. Block footprint: 30.0 mm in X × 12.0 mm in Y. Block height: 22.0 mm in Z.
7. Block is centered on X = 0 and Y = 0. Base face at Z = 0.

### 3. Cradle slot (the one functional interface)

8. Slot axis runs along Y, through the full 12.0 mm depth, centered at X = 0.
9. Slot radius `R` = `pole_d / 2 + fit_clearance` (= 10.3 mm now).
10. Slot arc center at Z = `center_height + fit_clearance` (= 18.3 mm now). **This offset is the load-bearing physics:** the pole rests on the slot bottom, so pole center Z = slot center Z − R + pole_d/2 = `center_height` exactly. Do not put the slot center at 18.0.
11. Slot shape in the XZ section: full semicircle of radius R below the slot center, then vertical walls (gap width = 2R = 20.6 mm now) from the slot center straight up through the top face. Result: the pole drops in from above with 0.6 mm total diametral clearance and nests in a near-matching curved cradle — no edge or point contact.
12. Slot bottom lands at Z = `center_height − pole_d/2` (= 8.0 mm now); at least 8 mm of solid plastic stays under the pole. Walls beside the slot are (30.0 − 2R)/2 = 4.7 mm thick now — if `pole_d` grows, grow block width X to keep walls ≥ 4.0 mm.
13. Add a 1.5 mm × 45° chamfer on the two top edges of the slot (where slot walls meet the top face), full Y length, as a drop-in lead-in.

### 4. Print orientation and economy

14. Model the part exactly as used: base flat on the bed (Z = 0), slot opening up, pole axis along Y. Do not rotate for printing.
15. This orientation has no downward-facing surfaces inside the slot — zero supports required. Verify: the only overhang candidates are the chamfers and the upward-facing slot valley, both printable.
16. Keep it minimal: no fillets, no ribs, no base flare, no holes, no text. The 12 mm Y depth and slicer infill are the plastic budget. Do not thicken anything beyond this spec.

### 5. Acceptance checks (assert these in the model or verify numerically)

17. Pole center height: slot bottom Z + pole_d/2 == 18.0.
18. Slot gap at top face = pole_d + 2 × fit_clearance (pole passes through).
19. Slot is centered at X = 0 (pole centered over the rest).
20. Bounding box = 30.0 × 12.0 × 22.0 with min corner at (−15, −6, 0).

---

The one number I'd flag for the record: 0.3 mm radial clearance is the standard drop-in fit for FDM. The height math in step 10 already compensates for it, so the 18.0 mm center height holds regardless of clearance choice.