Below is the build spec. I read the customer's numbers, worked out printed-fit clearances for a D-bore push fit, and pinned the geometry to the required bore-up print orientation.

---

# Build spec: `parts/valve_knob.py` — D-shaft valve knob

## 1. Overall form

1. One solid knob: a cylinder, 40 mm outer diameter, 18 mm tall, with six grip scallops cut into the rim and one blind D-bore on the vertical centerline.
2. No other features. No dome, no fillets except those named below, no text, no hub, no ribs. This keeps print time low.

## 2. Coordinate frame and print orientation (mandatory)

3. Model the part exactly as it prints. Z=0 is the print bed. The knob's closed face (the outer face the user sees in use) sits on the bed at Z=0. The bore opens straight up at Z=18.
4. The bore axis is the Z axis through (0, 0). The bore's flat wall faces +X (its plane normal points in −X, toward the axis).
5. Do not rotate the part for export. It must land on the bed as modeled.

## 3. Bore — the D-shaft interface (drives everything)

All shaft values come from `measurements.toml` and must stay parametric. Clearances are named constants in the file, not inlined magic numbers.

6. `bore_diameter = shaft_diameter + 0.2` → 8.2 mm. The 0.2 mm diametral clearance gives a snug push-on fit on FDM, which prints holes slightly undersized. Do not enlarge it; the customer wants no rattle.
7. Flat wall: cut the bore cylinder with a plane parallel to YZ at `x = (shaft_across_flat − shaft_diameter / 2) + 0.15` → x = +2.65 mm. The plane keeps material on the +X side (the bore cross-section is a D with the flat toward +X). The 0.15 mm flat clearance is tighter than the diametral clearance on purpose: this face carries all torque, and slop here makes the knob feel loose when turning.
8. Bore depth: 12.5 mm, blind, measured down from the top face (Z=18 to Z=5.5). The stem protrudes ~12 mm, so this leaves ~0.5 mm so the knob never binds against the valve body face; the D-flat engagement runs the full 12 mm.
9. Floor: the bore floor at Z=5.5 is flat and solid — 5.5 mm of material between floor and bed. Do not thin this.
10. Lead-in chamfer: 1.0 mm × 45° chamfer around the bore opening at the top face (Z=18), applied to the full D-profile edge including the flat. This is an upward-widening cone edge — printable, and it lets the user start the knob on the shaft without hunting.
11. Do NOT chamfer or fillet the bore floor or the flat wall's vertical edges.

## 4. Grip geometry

12. Six scallops: cylinders of 12 mm diameter, axes vertical (parallel to Z), full part height, centers evenly spaced every 60° on a circle of radius 24 mm from the part axis. Subtract them from the 40 mm body. Each scallop bites 2 mm into the rim, leaving a 6-lobe grip shape that works with wet hands.
13. Clock one scallop center on the +X axis so the grip pattern is symmetric about the flat.
14. Minimum wall check: nearest scallop surface to bore wall is >10 mm — no thin-wall risk; do not add reinforcement.

## 5. Print-friendliness constraints

15. Every surface is either vertical, flat-up, or flat-down. The only non-vertical feature is the bore chamfer, which opens upward. Zero supports required — verify no downward-facing overhang exists other than the flat bed face.
16. Bottom face (Z=0) is a full flat disc (minus scallops) for bed adhesion. Optionally add a 0.3 mm × 45° chamfer on the bottom outer edge to counter elephant's foot; nothing more.

## 6. Parametric requirements

17. Load `shaft_diameter` (8.0) and `shaft_across_flat` (6.5) from `measurements.toml`. They must remain the single source for the bore: changing either value in the file must correctly resize the bore diameter and relocate the flat with no other edits.
18. Define as named constants: `BORE_CLEARANCE = 0.2`, `FLAT_CLEARANCE = 0.15`, `BORE_DEPTH = 12.5`, `KNOB_DIAMETER = 40`, `KNOB_HEIGHT = 18`, `CHAMFER = 1.0`, scallop count/diameter/pitch radius.
19. Knob diameter, height, and scallop values are style parameters — hardcoded constants are fine, but keep them at the top of the file.

## 7. Acceptance checks (junior agent must verify before finishing)

20. Bore cross-section at any Z in [5.5, 17]: round side diameter 8.2 mm; distance from flat wall to the opposite (−X) bore wall = 6.85 mm (`shaft_across_flat + 0.15 + 0.1`); flat faces +X.
21. Bounding box ≈ 40 × 40 × 18 mm, part sits on Z=0, bore opening at max Z.
22. Part is a single watertight solid.

---

The two judgment calls worth flagging: I set the fit at +0.2 mm diametral / +0.15 mm on the flat, which is the standard snug push-fit band for FDM — if the customer's printer runs loose, the flat clearance is the number to shrink first. And I capped the knob at 40 × 18 mm: chunky enough for wet-hand torque on a hose valve, small enough to print in well under an hour with no supports.