# Vague-prompt pilot: no model passes a hobbyist prompt non-interactively

Every leaderboard task states every scored requirement. Real users do not talk like that. This pilot rewrote three function tasks (bundle_holder, pole_rest, valve_knob) as a hobbyist would ask for them, kept the scorer identical, and ran three arms at seed 13, three trials each, on 2026-08-29.

The vague instructions keep what a customer genuinely knows (the measured interfaces, the hardware they own, a frame note so the part lands in the fixture's axes) and drop everything else: tolerance bands, minimum faces and lengths, the volume ladder, the parameter-exposure requirement, the enumerated checks.

## Arms and results

| Arm | Setup | Mean score | Pass | Mean cost/part |
|---|---|---|---|---|
| A | grok-4.6 low, vague prompt | 0.639 | 0/9 | $0.39 |
| B | fable-5 writes a build spec (one shot, $1.13), grok-4.6 low executes | 0.625 | 0/9 | $1.42 |
| C | fable-5 medium, vague prompt | 0.667 | 0/9 | $2.90 |
| baseline | grok-4.6 low, real instruction (leaderboard) | — | 98% | $0.07 |
| baseline | fable-5 medium, real instruction (leaderboard) | — | 100% | $1.18 |

Every trial built, and most printed cleanly (lint 1.0 in arms A and B). The losses are functional dims and flex.

## What the pilot actually shows

1. **The gap is the prompt, not the model.** The smartest model tested (fable) scores within noise of the cheapest (grok) on vague prompts. Non-interactive one-shot design from a hobbyist prompt fails for everyone, at 4-40x the token cost of the same task cleanly specified.
2. **A written spec is not the missing ingredient.** Arm B's fable specs are genuinely good (the pole_rest spec derives the 0.25 mm arc-center offset that lands the pole at exactly the stated axis height), and where a spec pinned a graded number the executor hit it (arm B reached dims 1.0 on bundle_holder). But overall scores did not move, because most of the lost points are checks whose exact values are unknowable from the vague prompt: pole_rest dims sit at 0.46-0.54 in every arm, a constant, which measures the scorer, not the model.
3. **The flex stage is a convention, and only the instruction carries it.** grok wrote `measured("bundle_diameter")` and derived everything from it (parametric in spirit) but never exposed the keyword parameter the probes drive, so flex scored 0 in 17 of 18 grok-involved trials, and fable dropped it in 7 of 9 without the instruction line demanding it.

## Why these variants should NOT become leaderboard tasks as-is

The scorer grades stated requirements; the vague prompts delete the statements but keep the grading. That makes absolute scores unfair (a reasonable designer cannot converge on an arbitrary 20.0 minimum length) and only arm-to-arm comparisons valid. Shipping these as leaderboard rows would rank models on their luck at guessing deleted text.

## What a real "intake" task class needs

The pilot's implication: what separates models for real users is not one-shot geometry from vagueness (nobody can) but extracting the missing facts. A fair task class would be:

- **Oracle Q&A**: the runner holds the full fact sheet; the model may ask questions and the harness answers from the sheet, scripted. Score = final geometry through the existing gates, plus turn/question economy. Requires multi-turn harness plumbing (today's adapters are single-shot `-p` invocations).
- **Function-gates-only scoring** for whatever remains unstated: grade only checks any reasonable interpretation must satisfy (retention, fit, drop-in), never exact values the prompt no longer states.

## Layout

- `variants_vague/`: the three vague task shims (same scorer, swapped instruction)
- `gen_specs.py`, `specs/`: arm B's spec generator, the nine fable specs with per-call cost
- `results/`: one results.jsonl per arm
- `parts/`: every candidate part file, named `<arm>-<task>-<trial>.py`

Run on the contributor's own subscriptions; costs are API-list-price equivalents. Full transcripts retained locally, available on request.
