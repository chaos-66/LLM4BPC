"""Prepare the unified paper rerun. This module performs no network operations."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import prepare_sun_modality_eligibility_shots_v1 as isolation
import run_barrientos_ablation_suite_v2 as core
import run_v6_factorial_ablation_v1 as factorial
from bpc_hybrid.modality_benchmark import boundary, data, llm_se

NAME = "paper_e1_r19_v1"
LOCAL = ROOT / "outputs/development" / NAME
REPORT = ROOT / "outputs/reports" / (NAME + "_preflight.json")
OLD = "sun_modality_47bdd258ad450ccc"
NEW = "sun_modality_4af8b2f8b5ee7fe0"
OLD_HASH = "c21d486191aeda1b69d0cf4873607aa0af64b1a56203febaa95a67d690515af9"
NEW_HASH = "6f5a16b1cd44c3c47dbdc3584c69b5ba2b537ffd6460503ac587ddc616d717f1"
E1_HASH = "93e7a324a038792a18bd8cccfab0c3a3ddcff0477c3d0b3932c7d94773458fd9"
ESTG = ROOT / "data/input/estg150_formal_inference_input_v2.json"
GDPR = ROOT / "data/development/stage3_winter_paper_rerun_20261010_v1/regulation_sources.json"
GDPR_IDS = ROOT / "paper_experiments/04_gdpr_table_III_and_fig3/native_CR_records/LLM-SE.jsonl"
digest = boundary.digest


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")


def frozen(path, content):
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"frozen file differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def split_once(text, marker):
    if text.count(marker) != 1:
        raise ValueError(f"expected one component marker: {marker}")
    return text.split(marker, 1)


def variant_system(parent, full, arm):
    """Map worked demonstrations to E, added semantic guidance to S; J remains inherited."""
    guidance, material = split_once(full.removeprefix(parent), "\n\nCorpus modality demonstrations")
    first_shots, review = split_once(material, "\n\nModality review pass:")
    review, extra = split_once(review, "\n\nAdditional German training demonstrations")
    lead, contrasts = split_once(review, "\n   Synthetic contrasts, not corpus quotations:")
    examples, tail = split_once(contrasts, "\n\n3. Resolve what a negative expression denies.")
    e, s, _ = arm
    suffix = guidance if s == "1" else ""
    if e == "1":
        suffix += "\n\nCorpus modality demonstrations" + first_shots
    if s == "1":
        suffix += "\n\nModality review pass:" + lead
    if e == "1":
        suffix += "\n   Synthetic contrasts, not corpus quotations:" + examples
    if s == "1":
        suffix += "\n\n3. Resolve what a negative expression denies." + tail
    if e == "1":
        suffix += "\n\nAdditional German training demonstrations" + extra
    return suffix


def revised(train):
    path = ROOT / "outputs/development/sun_modality_es_minimal_v1/E1_system_prompt.txt"
    e1 = path.read_text(encoding="utf-8")
    old, new = train[OLD], train[NEW]
    if digest(e1.encode()) != E1_HASH or old.label != new.label or new.label != "definition":
        raise ValueError("parent prompt or original corpus labels differ")
    if [digest(r.text.encode()) for r in (old, new)] != [OLD_HASH, NEW_HASH]:
        raise ValueError("training texts changed")
    before, after = [f'19. "{r.text}" -> definition' for r in (old, new)]
    left, right = split_once(e1, before)
    return left + after + right


def datasets():
    estg = read(ESTG)["records"]
    gdpr = read(GDPR)["rules"]
    native_ids = gdpr_ids()
    return {
        "estg": [(r["sample_id"], r["approved_text_en"]) for r in estg],
        "gdpr": [(native_ids[r["rule_id"]], r["text"]) for r in gdpr],
        "german": data.load_split_text_only("test"),
    }


def gdpr_ids():
    with GDPR_IDS.open(encoding="utf-8") as handle:
        native = [json.loads(line) for line in handle]
    return {r["requirement_id"]: r["record"]["sample_id"] for r in native}


def make_bodies(pairs, full):
    base, _ = factorial._render_prompt("111", "placeholder", "placeholder")
    if not full.startswith(base + "\n\n"):
        raise ValueError("E1 no longer extends the frozen base system message")
    suffixes = {a: variant_system(base, full, a) for a in factorial.ALL_ARMS}
    if base + suffixes["111"] != full:
        raise ValueError("full prompt does not reproduce the single approved edit")
    bodies = {}
    for group, items in pairs.items():
        for arm in (factorial.ALL_ARMS if group == "estg" else ["111"]):
            loaded = factorial._load_generated_prompt(arm)
            system = loaded.system_prompt + suffixes[arm]
            examples = factorial._few_shot_block(loaded.raw_text)
            for sid, text in items:
                user = loaded.user_prompt_template.format(
                    sample_id=sid, source_id=sid, source_text=text, few_shot_block=examples)
                body = core._req_body(system, user)
                bodies[group, arm, sid] = body
    return bodies


def historical_controls(bodies, pairs):
    """Reuse two controls only after all 300 exact request fingerprints and raw responses match."""
    controls = {}
    for arm in ("000", "001"):
        path = ROOT / f"outputs/development/v6_factorial_ablation_v1/{arm}/repeat-01/raw_responses.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines()]
        seen = set()
        for r in rows:
            sid = r["sample_id"]
            key = ("estg", arm, sid)
            if (sid in seen or r["request_body_sha256"] != digest(encoded(bodies[key]))
                    or r["request_status"] != "ok" or not r["network_call"] or r["gate_error"]
                    or r["returned_model"] != llm_se.MODEL_ALIAS
                    or digest(r["raw_response_content"].encode()) != r["response_sha256"]):
                raise ValueError(f"incompatible historical control {key}")
            seen.add(sid)
            controls[key] = r
        if seen != {sid for sid, _ in pairs["estg"]}:
            raise ValueError(f"incomplete control {arm}")
    return controls


def build():
    pairs = datasets()
    if (any(len(rows) != len(dict(rows)) for rows in pairs.values()) or
            {g: len(rows) for g, rows in pairs.items()} != {"estg": 150, "gdpr": 33, "german": 426}):
        raise ValueError("input membership differs")
    train = {r.sample_id: r for r in data.load_split("train")}
    system = revised(train)
    base_report = read(ROOT / "outputs/reports/sun_modality_es_minimal_v1_preflight.json")
    ids = list(base_report["variants"]["E1"]["train_example_ids"])
    if len(set(ids)) != 22 or ids[18] != OLD or NEW in ids:
        raise ValueError("unexpected source example selection")
    ids[18] = NEW
    held = {"german_dev": data.load_split_text_only("dev"), "german_test": pairs["german"],
            "estg_source": [(r["sample_id"], r["raw_text_de"]) for r in read(ESTG)["records"]],
            "estg_input": pairs["estg"], "gdpr_input": pairs["gdpr"]}
    near = {}
    for split, texts in held.items():
        isolation.check_isolation([train[NEW]], texts)
        matched = []
        words = [(sid, isolation.tokens(t)) for sid, t in texts]
        for pos, tid in enumerate(ids, 1):
            a = isolation.tokens(train[tid].text)
            for sid, b in words:
                if isolation.near_match(a, b):
                    matched.append({"position": pos, "sample_id": sid})
        near[split] = matched
    bodies = make_bodies(pairs, system)
    controls = historical_controls(bodies, pairs)
    counts = Counter("/".join(key[:2]) for key in bodies if key not in controls)
    if len(bodies) != 1659 or len(controls) != 300 or sum(counts.values()) != 1359:
        raise ValueError("budget or request coverage differs")
    # Compare the new full user message against the actual E1 template independently.
    original = read(ROOT / "outputs/development/sun_modality_es_minimal_v1/E1_request_template.json")
    for group, items in pairs.items():
        for sid, text in items:
            reference = dict(original)
            reference["messages"] = [
                {"role":"system","content":system},
                {"role":"user","content":original["messages"][1]["content"].replace("{sample_id}",sid).replace("{source_text}",text)}]
            if bodies[group,"111",sid] != reference:
                raise ValueError(f"template drift: {group}/{sid}")
    hashes = {"|".join(key): digest(boundary.wire_bytes(body)) for key, body in bodies.items()}
    public = {
        "run_id": NAME, "phase": "offline_preflight", "api_calls_in_preflight": 0,
        "endpoint": "https://api.deepseek.com", "model": "deepseek-v4-pro",
        "settings": {k:v for k,v in original.items() if k != "messages"},
        "parent_system_sha256": E1_HASH, "revised_system_sha256": digest(system.encode()),
        "change": {"position":19,"old_id":OLD,"new_id":NEW,"original_label":"definition",
                   "old_text_sha256":OLD_HASH,"new_text_sha256":NEW_HASH},
        "fixed_input_sha256": {"estg":digest(ESTG.read_bytes()),"gdpr":digest(GDPR.read_bytes()),
                                "german":data.EXPECTED["test"]["sha256"]},
        "near_matches_after_edit":near, "number_of_examples":len(ids),
        "estimated_max_new_calls":sum(counts.values()),"new_calls_by_group":dict(counts),
        "historical_identical_controls": {"000":150,"001":150},
        "table_I_and_table_II_111":"one shared set of 150 predictions",
        "table_III_and_figure_3":"33 LLM-SE records; fixed previous checker, thresholds and baselines",
        "primary_german_denominator":426,
        "arm_fingerprints":{a:digest(encoded(bodies["estg",a,pairs["estg"][0][0]])) for a in factorial.ALL_ARMS},
        "requests_sha256":digest(encoded(hashes)), "automatic_retries":0,
        "gdpr_native_id_mapping_sha256":digest(encoded(gdpr_ids())),
        "sources_note":"Training text, complete requests, raw responses and sample predictions remain local.",
    }
    return public, pairs, bodies, controls


if __name__ == "__main__":
    plan, pairs, bodies, controls = build()
    frozen(REPORT, (json.dumps(plan,ensure_ascii=False,indent=2)+"\n").encode())
    print(json.dumps({k:plan[k] for k in ("revised_system_sha256","estimated_max_new_calls","new_calls_by_group","near_matches_after_edit")},ensure_ascii=False))
