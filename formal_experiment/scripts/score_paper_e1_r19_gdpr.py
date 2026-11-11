"""Replay the nine paper thresholds with frozen BPMNs, checker, model and evaluation."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs/reports/sun_formula_replay_20261014"
LOCAL = ROOT / "outputs/development/paper_e1_r19_v1"
PAPER = ROOT / "paper_experiments/04_gdpr_table_III_and_fig3"
SNAPSHOT = ROOT / "outputs/evidence/stage3_reproduction_repair_20261012_v1/source_snapshot/bpc_hybrid"
REVISION = "e8c3b32edf5434bc2275fc9bab85f82640a19130"
TYPES = ("missing_action","incorrect_actor","out_of_order")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen(path, obj):
    raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"prior output differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)


def run(historical):
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
    import spacy
    import torch
    torch.set_num_threads(2)
    package = types.ModuleType("bpc_hybrid")
    package.__path__ = [str(SNAPSHOT)]
    sys.modules["bpc_hybrid"] = package
    model_class = load("paper_sun_process",PAPER / "method/sun_model.py").SunProcessModel
    evaluation_v2 = load("paper_gdpr_evaluation", PAPER / "method/evaluation_v2.py")
    from bpc_hybrid.stage3_v2.checker_v2 import SharedStage3CheckerV2
    from bpc_hybrid.stage3_v2.rule_order_adapter_v3 import SharedRuleOrderAdapterV3
    from bpc_hybrid.stage3_v2.rule_record_converter_v2 import canonical_to_rule_record_v2
    from bpc_hybrid.stage3_v2.semantic_matcher_v2 import SharedSemanticMatcherV2, normalize_text_v2
    manifest = read(SOURCE / "manifest.json")
    code = PAPER / "method/sun_model.py"
    if hashlib.sha256(code.read_text(encoding="utf-8").encode()).hexdigest() != "ccc6758ef9c8b9e81011de8b06a0a1707571f6572fa9b8e8145a38699591b42f":
        raise ValueError("corrected checker differs")
    module = load("paper_local_mpnet", PAPER / "method/local_mpnet_backend_v1.py")
    modeldir = ROOT.parent / ".tmp/hf_cache/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots" / REVISION
    for name, sha in manifest["backend"]["artifact_sha256"].items():
        with (modeldir / name).open("rb") as handle:
            actual = hashlib.file_digest(handle,"sha256").hexdigest()
        if actual != sha:
            raise ValueError(f"MPNet dependency differs: {name}")
    backend = module.LocalMPNetBackend(modeldir)
    cache = read(SOURCE / "similarity_cache.json")
    if backend.identity() != cache["backend"]:
        raise ValueError("embedding backend identity differs")
    nlp = spacy.load("en_core_web_sm")
    if nlp.meta["version"] != manifest["nlp_model_version"] or spacy.__version__ != manifest["nlp_version"]:
        raise ValueError("NLP runtime differs")
    sources = {r["rule_id"]:r["text"] for r in read(PAPER / "requirements_33.json")["rules"]}
    filename = PAPER / "native_CR_records/LLM-SE.jsonl" if historical else LOCAL / "local_only/gdpr_native.jsonl"
    with filename.open(encoding="utf8") as handle:
        native = {r["requirement_id"]:r["record"] for r in map(json.loads,handle)}
    if set(native) != set(sources) or len(native) != 33:
        raise ValueError("GDPR native extraction incomplete")
    adapter = SharedRuleOrderAdapterV3(SharedSemanticMatcherV2(backend))
    ours = {rid:canonical_to_rule_record_v2(record,sources[rid],rid,nlp,order_adapter=adapter) for rid,record in native.items()}
    saved = read(PAPER / "rule_records.json")
    if historical:
        for rid, row in ours.items():
            if any(row[k] != saved["ours"][rid][k] for k in ("actions","actors","actor_action_pairs","order_relations")):
                raise ValueError(f"historical conversion differs: {rid}")
    rules = {"sun":saved["sun"], "ours":ours}
    matcher = SharedSemanticMatcherV2(backend)
    for pair in cache["pairs"]:
        if pair["key"][0] != matcher._identity_sha:
            raise ValueError("similarity cache has another model")
        matcher._cache[tuple(pair["key"])] = pair["similarity"]
    rows = read(ROOT / "paper_experiments/01_bpmn_process_records/process_records.json")
    models = {cid:model_class(row["process_id"],row,nlp) for cid,row in rows.items()}
    reference = read(PAPER / "development_reference.json")
    targets = [(c["case_id"],c["requirement_id"]) for c in reference["cases"]]
    if len(targets) != 115 or set(models) != {cid for cid,_ in targets}:
        raise ValueError("benchmark population differs")
    checker = SharedStage3CheckerV2(matcher,nlp,tau=.8,gamma=.55,theta=.45)
    texts = {t for v in rules.values() for r in v.values() for t in r["actions"] + r["actors"]}
    for m in models.values():
        texts.update(a["name"] for a in m.actions if a["name"])
        texts.update(m.actors)
        texts.update(b["object"] for b in m.business_objects)
    backend.embed(sorted({normalize_text_v2(checker.scorer._lemma(t)) for t in texts if t}))
    figure_points = [(.55,.45)] + [(g,.45) for g in (.35,.45,.65,.75)] + [(.55,t) for t in (.25,.35,.55,.65)]
    grid = read(PAPER / "threshold_selection.json")["grid"]
    points = figure_points if historical else list(dict.fromkeys(figure_points + list(itertools.product(grid["gamma"],grid["theta"]))))
    scores, grid_scores = [], []
    for gamma,theta in points:
        checker.set_thresholds(gamma=gamma, theta=theta)
        actual = {m:{cid:checker.check_rule_record(rule[rid],models[cid]) for cid,rid in targets}
                  for m,rule in rules.items()}
        actual = json.loads(json.dumps(actual))
        if (gamma,theta) in figure_points:
            expected = read(SOURCE / f"fig3_replay/predictions/signals_gamma_{gamma:.2f}_theta_{theta:.2f}.json")["signals"]
            for method in (("sun","ours") if historical else ("sun",)):
                if actual[method] != expected[method]:
                    raise ValueError(f"historical signal mismatch at {gamma}/{theta} for {method}")
        metrics = {m:evaluation_v2.evaluate_dev_method(m, reference["cases"],
                    {(m,cid,t):row[t] for cid,row in signal.items() for t in TYPES},reference["order_scope"])
                   for m,signal in actual.items()}
        for method,m in metrics.items():
            overall = m["overall"]
            positive = negative = tp = fp = 0
            for case in reference["cases"]:
                for typ in TYPES:
                    if typ == "out_of_order" and reference["order_scope"].get(case["requirement_id"]) != "TYPE_A_explicit_action_precedence":
                        continue
                    gold = case["reference_states"].get(typ)
                    alarm = actual[method][case["case_id"]][typ]["status"] == "violated"
                    positive += gold == "violated"
                    negative += gold == "satisfied"
                    tp += gold == "violated" and alarm
                    fp += gold == "satisfied" and alarm
            if (positive,negative,tp,fp,positive-tp) != (69,132,overall["TP"],overall["FP"],overall["FN"]) or overall["scored_cells"] != 201:
                raise ValueError("independent counts disagree")
        if (gamma,theta) in figure_points:
            scores.append({"gamma":gamma,"theta":theta,"methods":{k:v["overall"] for k,v in metrics.items()}})
            if not historical:
                frozen(LOCAL / f"local_only/gdpr_signals_{gamma:.2f}_{theta:.2f}.json",actual)
        if not historical and gamma in grid["gamma"] and theta in grid["theta"]:
            rank = evaluation_v2.calibration_tie_break_key("mpnet",metrics,gamma=gamma,theta=theta)
            grid_scores.append({"gamma":gamma,"theta":theta,"selection_key":rank})
    if historical:
        frozen(LOCAL / "historical_gdpr_validation.json", {"settings":len(scores),"signals_checked":9*115*3*2,"baseline":scores[0],"passed":True})
    else:
        winter = read(PAPER / "table_III.json")["methods"]["Winter"]
        frozen(ROOT / "outputs/reports/paper_e1_r19_v1_gdpr.json",{
            "scope":"GDPR development at previously frozen paper thresholds","population":201,
            "sun_and_ours":scores[0]["methods"],"Winter":winter,"figure_3":scores,
            "secondary_development_grid_fixed_mpnet":{"count":len(grid_scores),
                "best":max(grid_scores,key=lambda row:row["selection_key"]), "points":grid_scores}})
    print("GDPR verification complete",len(scores),"threshold settings",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("historical","score"))
    run(parser.parse_args().mode=="historical")
