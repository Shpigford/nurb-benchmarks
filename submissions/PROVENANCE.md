# Aliases replaced with resolved model ids, 2026-08-24

Fifteen runs recorded a floating model name (`fable`, `sonnet`, `haiku`, `opus`) instead of a pinned id, because they ran before the `harness.py` change that captures `modelUsage`. The alias was whatever the contributor typed, and nothing wrote down which model answered. Rows pool on the model string, so the board rendered one model as two: a `fable` row beside a `claude-fable-5` one, and four Claude models a submission under a pinned id away from splitting the same way.

The transcripts kept what the rows did not. Running the current `ClaudeCode.usage()` over each stored transcript returns the same `modelUsage` map the runner reads today, so every id below is recovered from the run's own artifacts, not inferred from the alias. Each run was rewritten only after the expected id appeared in the `modelUsage` of every one of its rows.

| alias | resolved to | runs | rows |
|---|---|--:|--:|
| `fable` | `claude-fable-5` | 1 | 6 |
| `sonnet` | `claude-sonnet-5` | 6 | 36 |
| `haiku` | `claude-haiku-4-5` | 5 | 27 |
| `opus` | `claude-opus-5` | 1 | 6 |

In every run, `model` was set to the resolved id, `usage.models` was backfilled with the full served set (each carries a `claude-haiku-4-5` sidechain alongside its primary), and the directory was renamed to the `<harness>-<model>-<effort>-<id>` the wizard would generate today. Scores, stages, timings, token counts, transcripts, and part sources are untouched.

## The one run that also needed its revision restamped

`claude-claude-fable-5-high-b523a2` was graded under `28728fea0e2f` (cable_clip), `e60a6422d46a` (bit_block), `4eb71d63bef3` (bundle_holder), `d2dc4e75efc7` (pole_rest), `2498e1db7385` (valve_knob), and `ea00b7650ef5` (leg_cup). It is the only alias run that covers the same six tasks as a later run of the same model at the same effort, so leaving those revisions in place would have kept the two rows apart on the page for a reason that no longer exists.

Two inputs to that digest moved between the two runs: the `modelUsage` capture that caused this whole problem, and a crash guard in `leg_cup/task.py` for an empty probe region. Neither touches a rubric, and re-grading all six parts under the current revisions reproduces every committed score and stage exactly, valve_knob's 0.675 included, so the rows carry the current revisions.

The other fourteen runs keep theirs. They cover tasks their same-model siblings did not, so nothing had to merge, and several ran against nurb 0.10.0 under an older CLI. That is a real difference in what the model was working with, and the report separates rows on it deliberately.

## Checking any of this

For the model ids, run `ClaudeCode().usage()` over a run's `transcript.txt` files and read `models`. For a score, materialize the task at seed 13, drop the submitted part in, restore that run's `measurements.toml` for leg_cup, and grade.

# The valve_knob centerline was the bounding box, 2026-08-27

`valve_knob` tells the model that "the bore opens straight up, on the part's vertical centerline". The scorer read that centerline as the centre of the part's bounding box and drove its virtual D-stem down from there. The two are the same point only when the outline is symmetric about the bore. A knob with three lobes, five lobes, one lobe, or a lever arm is not: the box centre sits off the axis, by 10 mm on the worst part in the corpus, and the stated fit clearance leaves 0.15 mm of radial room. So the stem went down a line the bore never occupied and jammed on the way in, on knobs that would spin freely on a real valve stem. The same centre fed the grip measurement, where an off-axis origin reads one side of a lobed outline as narrower than the knob ever is in the hand.

Lobe-count parity was the tell. An even count puts the box centre back on the axis and grades correctly; an odd count moves it off and loses the fit gate no matter how well the bore is cut. The defect could only ever take points away. A bore already on the box centre was graded from exactly the point it is graded from now, and a drive line that misses the bore cannot turn a bad bore into a good one.

`_centerline()` in `tasks/valve_knob/task.py` now finds the bore itself. It takes the Z-parallel cylindrical face that turns its back on its own axis, which is what separates a hole from a lobe, that reaches into the column the stem is driven down, and whose radius is nearest the stem's. That axis is exact where a section's centroid is only close: the centroid of a D-profile sits about 0.45 mm toward the round side on this seed, which is already more than the fit check allows. A part with no such face keeps the bounding-box centre, so the behavior stays defined. Two submitted knobs clip their D-bore with a box that lands in the wrong place and are left with a sliver where the socket should be; both still fail the fit check, one from its recovered axis and one from the fallback.

All 122 committed `valve_knob` rows were re-graded under the fixed scorer. 24 moved, 21 of them from a sub-1.0 score to exactly 1.0. The other three still fail a real gate and only score nearer it. 76 rows were already at 1.0 and not one lost a point, and the 98 rows whose box centre already sat on the bore axis scored identically to the digit.

| run | trials | score |
|---|---|---|
| `claude-claude-fable-5-high-b523a2` | 1 | 0.675 to 1.0 |
| `claude-claude-fable-5-medium-37a1d1` | 2, 3 | 0.675 to 1.0, 0.675 to 1.0 |
| `claude-claude-opus-5-high-2a112c` | 2 | 0.7063 to 1.0 |
| `claude-claude-opus-5-medium-5a54e9` | 1, 2, 3 | 0.675 to 1.0, 0.675 to 1.0, 0.675 to 0.7688 |
| `claude-claude-sonnet-5-high-92d835` | 2, 3 | 0.675 to 1.0, 0.675 to 1.0 |
| `claude-claude-sonnet-5-low-ab6041` | 3 | 0.675 to 1.0 |
| `codex-gpt-5.6-terra-high-fedcec` | 1, 2, 4, 5 | 0.675 to 1.0, 0.675 to 1.0, 0.675 to 1.0, 0.675 to 1.0 |
| `codex-gpt-5.6-terra-low-70e660` | 2 | 0.675 to 0.7063 |
| `codex-gpt-5.6-terra-medium-3ab9a7` | 1, 2, 3 | 0.675 to 0.7063, 0.675 to 1.0, 0.675 to 1.0 |
| `codex-gpt-5.6-terra-medium-d94a80` | 2 | 0.675 to 1.0 |
| `grok-grok-4.6-high-89d888` | 3 | 0.675 to 1.0 |
| `grok-grok-4.6-medium-c4f223` | 1 | 0.7063 to 1.0 |
| `grok-grok-4.6-medium-cb0291` | 2, 3 | 0.675 to 1.0, 0.7063 to 1.0 |
| `grok-grok-4.6-xhigh-5c427e` | 1 | 0.675 to 1.0 |

Every `valve_knob` row now carries `3202508a30f9`, the revision the fixed task file produces, in place of the four revisions the corpus had accumulated. `score`, `stages`, and `benchmark_revision` are the only fields that moved, and only on `valve_knob` lines. Transcripts, timings, token counts, harness and nurb versions, seeds, trial numbers, part sources, and every `measurements.toml` are untouched, and the rows for the other five tasks are byte-identical.

## Checking any of this

Grade a submitted part the way `run.py` does, with `grade.run("submissions/<run>/valve_knob/trial_<n>/project/parts/valve_knob.py", "tasks/valve_knob", 13)`. Each committed `project/` already carries the `measurements.toml` the scorer reads next to the part. To see the defect rather than the fix, check out the parent of this commit and grade the same part: a row in the table above fails there with "the stem does not fit", and grades clean here.
