"""Vague-prompt variant: same scorer, hobbyist instruction. Local experiment only."""
import dataclasses, importlib.util, pathlib

_BASE = pathlib.Path(__file__).resolve().parents[2] / "tasks" / "valve_knob" / "task.py"
_spec = importlib.util.spec_from_file_location("_nurb_eval_task_base_valve_knob", _BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
globals().update({k: v for k, v in vars(_base).items() if not k.startswith("__")})

VAGUE_INSTRUCTION = """Design a part and save it as parts/valve_knob.py.

Customer request, in their own words:

"The plastic handle on my hose valve snapped off and I want to print a replacement
knob. The stem is a D-shaft; I measured it: shaft_diameter and shaft_across_flat in
measurements.toml ({shaft} mm across, {flat} mm across the flat). It sticks out
about 12 mm from the valve body. The knob needs to push onto the stem snugly, no
rattle, but I don't want to hammer it on, and it obviously has to actually turn the
valve instead of spinning on the stem. Make it chunky enough to grip with wet hands.
Prints without supports."

Modeling frame, so your part lines up with the customer's fixture: model the knob
bore-up as it prints, bore opening straight up on the part's vertical centerline,
with the stem's flat facing +X.
"""

def instance(seed):
    inst = _base.instance(seed)
    return dataclasses.replace(inst, instruction=VAGUE_INSTRUCTION.format(**inst.dims))
