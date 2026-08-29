## Build spec: parts/pole_rest.py — drop-in pole rest

**Form summary.** One solid rectangular block. A concave circular groove is cut into the top, running the full length of the block. The pole drops into the groove from above and rests on a conforming curved surface. Overall size approx 26.5 mm (X) x 15 mm (Y) x 18.25 mm (Z).

### 1. Coordinate frame and print orientation

1.1. The pole axis runs along Y. The groove runs along Y for the full part length.
1.2. The bottom face of the block sits flat on the bed at Z = 0. The part prints in its use orientation. Do not rotate it.
1.3. Center the part on X = 0. The groove centerline is at X = 0 (customer requires the pole centered over the rest).

### 2. Parameters (define these as named variables in the file)

2.1. `pole_diameter` — read from `measurements.toml` (`pole_diameter`, currently 20.0). Never hardcode 20.0.
2.2. `center_height = 18.0` — pole center above the bench. This matches the customer's existing fixture row. Hardcode it as a named constant with a comment; it is a fixture requirement, not a measurement.
2.3. `radial_clearance = 0.25` — printed drop-in fit clearance, per side.
2.4. `wall = 3.0`, `length_y = 15.0` — non-critical, may stay literals.

All Z-critical dimensions below must be computed from these parameters, so a re-measured pole regenerates a correct part.

### 3. Groove geometry (the only critical feature)

3.1. Groove cross-section (in XZ): a circular arc of radius `groove_r = pole_diameter/2 + radial_clearance` = 10.25 mm.
3.2. Arc center: X = 0, Z = `center_height − pole_diameter/2 + groove_r` = 18.25 mm.
3.3. Groove floor (lowest point of the arc) is therefore at Z = `center_height − pole_diameter/2` = 8.0 mm exactly. The pole rests on the floor, so its center lands at Z = 18.0 regardless of clearance. Do not let clearance shift this floor height.
3.4. Top of the block = arc center height = 18.25 mm. Stop the groove walls exactly at the arc center height, never above it. Above that height the arc re-closes and the pole cannot drop in. Mouth width at the top is then 2 x 10.25 = 20.5 mm, giving 0.25 mm per side for insertion.
3.5. Because `groove_r` exceeds the pole radius by only 0.25 mm, the pole is cradled on a near-conforming curved surface, not on edges or points. Do not substitute a V-groove or two rails.
3.6. Lead-in: chamfer both top inner edges of the mouth at 2.0 mm x 45°, flaring outward/upward. This keeps the wet finish off the sharp mouth edges during drop-in.

### 4. Block body

4.1. Outer width (X): `pole_diameter + 2*radial_clearance + 2*wall` = 26.5 mm.
4.2. Length (Y): 15.0 mm. Groove runs the full length; both Y end faces are open (the pole passes over both ends).
4.3. Height (Z): 18.25 mm per 3.4. There is 8.0 mm of solid material under the groove floor; leave it solid. No ribs, shells, holes, or pockets — the slicer's infill handles material economy.
4.4. No fillets or chamfers other than 3.6. No text, no logos.

### 5. Printability checks (must all hold)

5.1. Bottom face is a single flat rectangle on Z = 0.
5.2. Every groove surface faces upward (concave cut from the top); the steepest wall tangent is vertical at the mouth. Zero overhangs beyond vertical, zero bridges, zero supports.
5.3. One part per file. Do not array multiple rests; the customer prints copies via the slicer.

### 6. Acceptance criteria

6.1. Lowest point of groove at Z = 8.0 (with `pole_diameter` = 20.0).
6.2. Mouth opening 20.5 mm wide at Z = 18.25, symmetric about X = 0.
6.3. Changing `pole_diameter` in measurements.toml moves the groove floor so pole center stays at Z = 18.0.
6.4. A 20.0 mm cylinder along Y, center at (0, y, 18.0), fits the groove with 0.25 mm radial gap and does not intersect the part.