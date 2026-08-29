"""Vague-prompt variant: same scorer, hobbyist instruction. Local experiment only."""
import dataclasses, importlib.util, pathlib

_BASE = pathlib.Path(__file__).resolve().parents[2] / "tasks" / "pole_rest" / "task.py"
_spec = importlib.util.spec_from_file_location("_nurb_eval_task_base_pole_rest", _BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
globals().update({k: v for k, v in vars(_base).items() if not k.startswith("__")})

VAGUE_INSTRUCTION = """Design a part and save it as parts/pole_rest.py.

Customer request, in their own words:

"I finish poles and dowels and need little rests to lay them across while the finish
dries. A row of identical printed rests sits on the bench. The pole I'm doing now
measured {pole} mm across; it's pole_diameter in measurements.toml. The other rests
in the row hold the pole's center exactly {axis_h} mm above the bench, centered over
the rest, so this one has to match. The finish stays soft for a while, so it can't
sit on edges or points; it needs to be properly cradled. I want to drop the pole in
from above, not thread it through. Cheap on plastic, prints flat, no supports."

Modeling frame, so your part lines up with the customer's fixture: the pole runs
along Y, the bench is the bed (down is -Z), and the part prints as it is used.
"""

def instance(seed):
    inst = _base.instance(seed)
    return dataclasses.replace(inst, instruction=VAGUE_INSTRUCTION.format(**inst.dims))
