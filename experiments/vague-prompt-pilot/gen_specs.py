"""Arm B stage 1: Fable turns each vague request into a build spec, one call per trial."""
import json, pathlib, subprocess, sys, tempfile

sys.path.insert(0, "src")
from nurb_evals import scoring

TASKS = ["bundle_holder", "pole_rest", "valve_knob"]
SEED = 13

SPEC_PROMPT = """You are the design lead for a CAD service. A customer described a part they need \
printed. A junior CAD agent will build it with nurb (Python parametric CAD for 3D printing) \
in a project where the customer's measurements are already on file in measurements.toml. \
The junior agent is competent at executing precise instructions but does not infer intent: \
anything you leave vague, it will get wrong.

Write an implementation-ready build spec for this part. State: overall form and rough \
dimensions; exact orientation on the bed; every functional interface with real numbers \
(clearances for printed fits, screw/bore physics for named hardware, contact geometry); \
which measurements.toml entries drive which dimensions and which values must stay \
parametric; what to keep minimal so it prints fast without supports. Use millimeters. \
Do not write code. Be complete but tight: a numbered spec the junior agent can follow \
without asking questions.

Customer request:

{request}

The project's measurements.toml already contains:

{measurements}"""

SHIM = '''"""Spec-augmented vague variant: same scorer, Fable-written spec appended. Local experiment."""
import dataclasses, importlib.util, pathlib

_BASE = pathlib.Path(__file__).resolve().parents[3] / "tasks" / "{task}" / "task.py"
_spec = importlib.util.spec_from_file_location("_nurb_eval_task_base_{task}", _BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
globals().update({{k: v for k, v in vars(_base).items() if not k.startswith("__")}})

_VAGUE_DIR = pathlib.Path(__file__).resolve().parents[3] / "variants_vague" / "{task}"
_vspec = importlib.util.spec_from_file_location("_nurb_eval_task_vague_{task}", _VAGUE_DIR / "task.py")
_vague = importlib.util.module_from_spec(_vspec)
_vspec.loader.exec_module(_vague)

_SPEC_TEXT = (pathlib.Path(__file__).parent / "spec.md").read_text(encoding="utf-8")

def instance(seed):
    inst = _vague.instance(seed)
    combined = (
        inst.instruction
        + "\\n\\nYour design lead already turned this request into a build spec. Follow it:\\n\\n"
        + _SPEC_TEXT
    )
    return dataclasses.replace(inst, instruction=combined)
'''

out_root = pathlib.Path("variants_spec")
empty = pathlib.Path(tempfile.mkdtemp(prefix="nurb-specgen-"))
total = 0.0
for task in TASKS:
    mod = scoring.load_task(f"variants_vague/{task}")
    inst = mod.instance(SEED)
    prompt = SPEC_PROMPT.format(request=inst.instruction, measurements=inst.measurements)
    for n in (1, 2, 3):
        dest = out_root / f"t{n}" / task
        dest.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", "claude-fable-5", "--output-format", "json"],
            capture_output=True, text=True, timeout=600, cwd=empty,
        )
        data = json.loads(r.stdout)
        spec = data["result"]
        cost = data.get("total_cost_usd", 0.0)
        total += cost
        (dest / "spec.md").write_text(spec, encoding="utf-8")
        (dest / "meta.json").write_text(json.dumps(
            {"cost_usd": cost, "duration_ms": data.get("duration_ms"),
             "usage": data.get("usage")}, indent=2), encoding="utf-8")
        (dest / "task.py").write_text(SHIM.format(task=task), encoding="utf-8")
        print(f"{task} t{n}: ${cost:.3f}, {len(spec)} chars", flush=True)
print(f"TOTAL spec cost: ${total:.2f}")
