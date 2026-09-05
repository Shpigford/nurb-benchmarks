"""Vague-prompt variant: same scorer, hobbyist instruction. Local experiment only."""
import dataclasses, importlib.util, pathlib

_BASE = pathlib.Path(__file__).resolve().parents[2] / "tasks" / "bundle_holder" / "task.py"
_spec = importlib.util.spec_from_file_location("_nurb_eval_task_base_bundle_holder", _BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
globals().update({k: v for k, v in vars(_base).items() if not k.startswith("__")})

VAGUE_INSTRUCTION = """Design a part and save it as parts/bundle_holder.py.

Customer request, in their own words:

"I've got a cable bundle running along the wall behind my bench and I'm tired of it
sagging. I want to print a little holder that screws to the wall; I've got M4
pan-head screws. I measured the bundle with calipers: it's the bundle_diameter entry
in measurements.toml ({bundle} mm). The cables need to slide in along the wall and
then stay put. Don't waste plastic, and it needs to print without supports."

Modeling frame, so your part lines up with the customer's fixture: the wall is the
plane at your part's minimum X (flat back face against it), the bundle runs along Y,
down is -Z, and the part prints in its mounted orientation.
"""

def instance(seed):
    inst = _base.instance(seed)
    return dataclasses.replace(inst, instruction=VAGUE_INSTRUCTION.format(**inst.dims))
