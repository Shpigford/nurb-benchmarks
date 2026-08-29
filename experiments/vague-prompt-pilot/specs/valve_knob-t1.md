Build spec for `parts/valve_knob.py` — push-on D-bore valve knob. Numbered, all dimensions in mm.

## Valve Knob — Build Spec

**Overall form:** a squat cylinder, Ø38 × 17 tall, with six finger scallops around the rim and a blind D-shaped bore down the center. One solid, no moving parts.

### 1. Modeling frame and print orientation
1.1. Model the knob as it prints: the closed end (the knob's decorative top, in use) sits flat on the bed at z = 0; the bore opens straight up at the top of the part.
1.2. Bore axis = the part's vertical centerline (the Z axis).
1.3. The D-flat of the bore faces +X (flat plane normal is +X).
1.4. Every cut (bore, scallops) is vertical, so the part prints with zero supports and zero overhangs. Do not add any feature with a downward-facing surface.

### 2. Body
2.1. Base solid: cylinder, `knob_diameter` = 38.0, `knob_height` = 17.0, centered on Z, sitting on z = 0.
2.2. Grip: 6 scallops, equally spaced (60° apart). Each scallop is a vertical cylinder cut, Ø12.0, with its axis at radius 23.0 from center (so each bite is ~4 mm deep). Full height of the body.
2.3. Do not add knurling, text, top domes, or fillets on load paths. Chamfers only (§5). Keep the body a single extrusion-like solid so it slices fast.

### 3. Bore (the only functional interface)
3.1. Blind D-pocket cut from the top face (z = `knob_height`) downward.
3.2. Bore depth = 13.0 (stem protrusion 12.0 + 1.0 slack so the knob seats on the valve body, not on the stem tip). Floor thickness below the bore = 4.0. These two must sum to `knob_height` (13 + 4 = 17).
3.3. Bore cross-section: circle of diameter `shaft_diameter + fit_clearance`, truncated by one plane so the across-flat dimension is `shaft_across_flat + fit_clearance`.
3.4. `fit_clearance` = 0.20 diametral. This is the printed push-on snug fit: firm hand press, no hammer, no rattle. It applies once to the diameter and once to the across-flat (not per side).
3.5. Nominal numbers at defaults: bore Ø8.20; across-flat 6.70. The flat plane sits at x = +( (`shaft_across_flat` + `fit_clearance`) − (`shaft_diameter` + `fit_clearance`)/2 ) = +2.60, normal +X. The round side of the bore is toward −X. Torque transfers through this flat — it is what stops the knob spinning on the stem, so never round or shrink it.
3.6. Add a 1.0 × 45° lead-in chamfer on the bore mouth (the top opening), on both the round wall and the flat, to guide the push-on.
3.7. Minimum wall around the bore at the flat side is (38/2 − 2.6) ≈ 16 mm — no thin-wall risk; do not add a boss.

### 4. Parametric wiring (measurements.toml)
4.1. `shaft_diameter` (8.0) → bore circle diameter, per §3.3. Read from measurements.toml; never hardcode.
4.2. `shaft_across_flat` (6.5) → flat-plane position, per §3.3/3.5. Read from measurements.toml; never hardcode.
4.3. Function keyword parameters (viewer sliders), plain-word names with one-line docstring descriptions: `fit_clearance` = 0.2 (extra bore room for a snug push-on), `knob_diameter` = 38.0, `knob_height` = 17.0, `bore_depth` = 13.0, `grip_scallop_diameter` = 12.0. Stem measurements are facts, not sliders — they stay out of the parameter list.

### 5. Polish
5.1. Standard 1 mm chamfer pass on exposed edges (top rim, scallop edges, bed-edge). Keep the template's closing `polish` step. No crowns, no unprompted rounding.

### 6. Verify before handoff
6.1. `nurb check` clean, no supports flagged.
6.2. `nurb inspect`: confirm the bore floor is 4.0 thick and the flat plane is at x = +2.60 at defaults.
6.3. Confirm one flat bed face at z = 0 and bore opening up.

The only number I chose without customer data is `fit_clearance` = 0.2 — a standard printed clearance for a snug FDM push-on. It is a slider, so if the first print is loose or tight, the customer adjusts one value and reprints.