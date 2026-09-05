`nurb rules` needs approval I can't get in this autonomous run, so the spec below uses standard FDM fit doctrine. Here is the build spec for the junior agent.

---

# Build spec: `parts/valve_knob.py` — D-shaft valve knob

## Form and orientation

1. **Overall form.** One solid: a cylindrical knob, ~Ø35 mm × 17 mm tall, with finger scallops around the rim and a blind D-profile bore up the center. No other bodies.

2. **Bed orientation (model it this way, it prints this way).** Closed top face of the knob sits on the bed at z = 0. Knob axis is +Z. Bore opening faces straight up, centered on the Z axis at the top of the part. The flat of the D faces **+X**. Every surface is vertical, flat, or chamfered ≤ 45°. Zero supports.

## Bore (the functional interface)

3. **Bore profile.** Circle of diameter `shaft_diameter + bore_clearance` = 8.0 + 0.2 = **Ø8.2 mm**, centered on the Z axis, cut by one flat plane normal to +X. Place the flat so the round-side-to-flat distance of the bore equals `shaft_across_flat + flat_clearance` = 6.5 + 0.15 = **6.65 mm**. That puts the flat plane at **x = +2.55 mm** (= 6.65 − 8.2/2). The flat is what transmits torque; do not rely on friction.

4. **Clearances are parameters, not literals.** `bore_clearance = 0.2` and `flat_clearance = 0.15` are keyword defaults with plain-word docstring lines (e.g. `bore_clearance: extra bore width for push fit; raise if tight, lower if it rattles`). These are the sliders the customer tunes after the first test fit. 0.2/0.15 targets a snug push-on for a vertical FDM hole: firm hand push, no mallet, no rattle.

5. **Bore depth.** Blind bore, depth **13.0 mm** from the top face (= `stem_length` 12.0 + 1.0 slack). The slack guarantees the knob seats against the valve body, never bottoms on the stem tip. `stem_length = 12.0` stays a parameter — the customer said "about 12 mm."

6. **Bore floor.** Solid floor of **4.0 mm** below the bore. Total knob height = 13.0 + 4.0 = **17.0 mm**. The floor is at the bed side, so the bore has no bridge and no support.

7. **Lead-in.** Chamfer the bore opening rim **1.0 mm × 45°**. It widens upward, so it prints clean, and it lets the customer start the D-shaft without hunting for alignment.

## Grip

8. **Body.** Cylinder `knob_diameter = 35.0` (parameter — pure taste). Cut **7** vertical half-round finger scallops, each Ø10 mm, evenly spaced, cylinder centers on a circle of radius 19.5 mm. Cut depth ≈ 2.0 mm each. Scallops run the full part height. This is the wet-hand grip; no knurling, no fillets, nothing fancier.

9. **Wall check.** Thinnest wall (scallop root to bore) ≈ 14.5 − 4.1 = **10.4 mm**. Ample for hand torque; confirm with `nurb inspect`, not by eye.

## Edges and finish

10. **Polish pass.** Keep the template's standing `polish` chamfer (1 mm) on exposed edges — scallop edges included. Chamfer, never round; no `crown`. Bottom (bed-side) outer edge gets 0.5 mm chamfer to kill elephant-foot.

## Parameters and data flow

11. **From `measurements.toml` (read, never hardcode):** `shaft_diameter` → bore circle; `shaft_across_flat` → flat position. **Keyword parameters with docstring lines:** `bore_clearance = 0.2`, `flat_clearance = 0.15`, `stem_length = 12.0`, `knob_diameter = 35.0`, `knob_height` derived (do not expose), `scallop_count = 7`. Nothing else parametric.

12. **Keep it minimal.** One solid, no assembly, no obstacles, no interior cavities. 17 mm tall with all-vertical walls is already a fast, supportless print; do not add height, ribs, or decoration.

## Verify before handoff

13. Run `nurb check` (must pass: no overhangs, no supports), `nurb inspect` to confirm bore diameter 8.2, flat at 6.65, thinnest wall ≥ 10 mm, and one face flat on the bed. Write the card; record in `## Don't`: no through-bore (floor keeps water out and gives a clean top face), no set screw (flat carries the torque), no rounded rim.