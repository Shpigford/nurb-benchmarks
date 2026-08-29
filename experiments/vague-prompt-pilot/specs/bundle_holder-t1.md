Build spec: `parts/bundle_holder.py` — wall-mount cable bundle J-channel.

**Design intent.** An open U-channel hook. The flat back mounts to the wall with one M4 pan-head screw. The bundle drops in from above, sliding down along the wall, past a small retention nub, into the channel. Gravity plus the nub hold it. Constant cross-section extruded along Y, so it prints in mounted orientation with zero supports.

**Parameters.** Let `D` = `bundle_diameter` from measurements.toml (currently 8.0). Every dimension below written in terms of `D` must stay parametric. Fixed constants: wall/feature thickness `t = 3.0`, part width `W = 10.0` (along Y).

1. **Coordinate frame.** Wall plane at X = 0 (back face flush against it). Bundle axis along Y. Down is −Z. Bed is the plane Z = 0; the part's bottom face sits on it. Part occupies Y = 0 to `W`.

2. **Overall form.** One 2D profile in the XZ plane, extruded `W` = 10.0 mm along Y. Rough envelope: 15 mm in X, 10 mm in Y, 24 mm in Z. No other bodies.

3. **Back plate.** X = 0 to 3.0 (`t`), Z = 0 to 24.0 (top edge = screw-hole center Z + 6.0; see item 7). Back face at X = 0 must be flat and unbroken except the screw hole.

4. **Channel floor.** Z = 0 to 3.0 (`t`), spanning X = 0 to `2t + D + 1.0` (= 15.0 for D = 8). It merges with the back plate at the corner.

5. **Outer lip.** X = `t + D + 1.0` to `2t + D + 1.0` (12.0 to 15.0), from Z = 3.0 up to Z = `t + D + 1.0` (= 12.0). This gives a channel cavity `D + 1.0` wide in X (1.0 mm total lateral clearance) and `D + 1.0` tall from floor to lip top, so the bundle (top at Z = `t + D` = 11.0) sits fully below the lip.

6. **Retention nub.** On the lip's inner face (X = 12.0 plane), at the lip top, full width in Y. Triangular cross-section: protrudes 0.8 mm in −X, with both the underside and topside at 45° (total nub height 1.6 mm, apex at Z = 12.0 − 0.8). Entry gap becomes `D + 0.2` = 8.2 mm; the taped bundle compresses past it and is then captured. The 45° underside is what makes it printable without support — do not make it steeper than 45° from vertical.

7. **Screw interface.** One through-hole in the back plate, axis along X, diameter 4.5 mm (M4 clearance for a printed part; nominal M4 is 4.0, DIN normal fit 4.5). Center at Y = `W/2` = 5.0, Z = lip top + 6.0 = `t + D + 7.0` (= 18.0 for D = 8). That Z puts the driver axis 6.0 mm above the lip top, so a screwdriver reaches the screw straight-on without hitting the lip. The pan head (Ø8.0, height 3.1) bears directly on the back plate's front face at X = 3.0 — no counterbore, no countersink. Keep ≥ 4.0 mm of plate above and beside the hole center (satisfied by the 24.0 plate top and `W` = 10).

8. **Printability rules.** Bottom face (Z = 0) is the only bed contact; keep it a single flat region. All vertical faces stay vertical; the only overhangs are the 45° nub and the 4.5 mm horizontal hole (bridges fine at that size). No fillets or chamfers anywhere else — they add nothing here.

9. **What stays parametric vs fixed.** Parametric on `D`: channel width `D + 1.0`, lip inner X position `t + D + 1.0`, lip top Z `t + D + 1.0`, nub gap `D + 0.2`, hole center Z `t + D + 7.0`, plate top `t + D + 13.0`. Fixed literals: `t = 3.0`, `W = 10.0`, hole Ø4.5, nub 0.8 mm at 45°.

10. **Do not add:** a closed loop (the bundle must drop in, not thread through), a second screw hole, ribs, or wall pads. Total plastic is ~3 mm walls throughout; that is the intent.