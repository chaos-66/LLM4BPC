"""An append-only reader-review branch; no inference or label postprocessing."""
import json

from . import boundary, fewshot

ROOT = boundary.ROOT
CONTRACT = ROOT / "configs/supplement/sun_modality_review_v1.json"


def read_contract():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for name in ("guidance", "parent_preflight", "parent_result", "error_review"):
        spec = contract[name]
        if boundary.digest((ROOT / spec["path"]).read_bytes()) != spec["sha256"]:
            raise ValueError("review branch binding mismatch: " + name)
    fewshot.read_contract()
    return contract


def request_body(sample_id, text, *, block=None):
    contract = read_contract()
    body = fewshot.request_body(sample_id, text, block=block)
    guidance = (ROOT / contract["guidance"]["path"]).read_text(encoding="utf-8").strip()
    body["messages"][0]["content"] += "\n\n" + guidance
    return body
