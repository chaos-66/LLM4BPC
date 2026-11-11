"""Offline replay and scoring of the same registered paper populations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_paper_e1_r19_v1 as pre
import run_paper_e1_r19_v1 as dispatch
from bpc_hybrid import formal_stage2_evaluation as stage2
from bpc_hybrid.sep_c3_primary_evaluation import evaluate_primary_view
from bpc_hybrid.modality_benchmark.metrics import evaluate

PAPER = pre.ROOT / "paper_experiments"
TABLE1 = PAPER / "02_estg150_table_I"
TABLE2 = PAPER / "03_estg150_table_II_ablation"
GERMAN = PAPER / "05_german_modality_426"
DEV = pre.ROOT / "outputs/development"
REPORTS = pre.ROOT / "outputs/reports"


def jsonlines(path):
    with path.open(encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def save(path, value):
    pre.frozen(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def population(rows, ids):
    found = [r["sample_id"] for r in rows]
    require(len(found) == len(set(found)) and set(found) == set(ids), "missing, duplicate or extra sample")


def stage2_metrics(arm, rows, gold):
    population(rows, [r["sample_id"] for r in gold["records"]])
    result = evaluate_primary_view(gold, stage2.predictions_to_evaluator(rows), method_id=arm)
    pooled = result["span"]["pooled_five_span_fields"]
    require(result["denominator"] == 150 and pooled["ground_truth"] == 824, "incorrect EStG population")
    return {"modality_macro_f1": result["modality_labels"]["macro_f1"],
            "span_fields": {f:{k:v[k] for k in ("extracted","f1","ground_truth","precision","recall")}
                            for f,v in result["span_fields"].items()},
            "pooled_five_span_fields": pooled}


def old_response(r):
    raw = r["raw_response_content"] or ""
    require(pre.digest(raw.encode()) == r["response_sha256"], "historical raw content changed")
    return {"raw_content":raw, "response_sha256":r["response_sha256"],
            "request_sha256":r["request_body_sha256"]}


def estg_replay(texts):
    gold = pre.read(TABLE1 / "shared/gold_150.json")
    table_1 = pre.read(TABLE1 / "table_I.json")["methods"]
    for name, expected in table_1.items():
        rows = pre.read(TABLE1 / f"predictions/{name}.json")["records"]
        require(stage2_metrics(name, rows, gold) == expected, f"Table I mismatch: {name}")
    manifest = pre.read(pre.ROOT / "outputs/evidence/g04_fine_gold_span_formal_results_v2/manifest.json")
    reference = pre.read(TABLE2 / "table_II.json")["arms"]
    scores = {}
    for arm, desc in manifest["inputs"]["table2_predictions"].items():
        path = (pre.ROOT / desc["path"]).with_name("raw_responses.jsonl")
        rows = [dispatch.canonical(("estg",arm,r["sample_id"]), texts[r["sample_id"]], old_response(r))
                for r in jsonlines(path)]
        archived = jsonlines(TABLE2 / f"predictions/{arm}.jsonl")
        population(archived, texts)
        projected = {r["sample_id"]:(r["request_status"],(r.get("record") or {}).get("clauses",[]))
                     for r in rows}
        for r in archived:
            require(projected[r["sample_id"]] ==
                    (r["request_status"], (r.get("record") or {}).get("clauses",[])),
                    f"historical EStG clauses differ: {arm}/{r['sample_id']}")
        measured = stage2_metrics(arm, rows, gold)
        require(measured["pooled_five_span_fields"]["f1"] == reference[arm]["overall_micro_f1"]
                and measured["modality_macro_f1"] == reference[arm]["modality_label_macro_f1"]
                and {f:v["f1"] for f,v in measured["span_fields"].items()} == reference[arm]["per_field_f1"],
                f"Table II mismatch: {arm}")
        scores[arm] = measured["pooled_five_span_fields"]["f1"]
    return {"table_I":{m:v["pooled_five_span_fields"]["f1"] for m,v in table_1.items()},
            "table_II":scores, "raw_responses_replayed":1200}


def german_metrics(labels, gold, omitted):
    require(set(gold) == set(labels), "German population differs")
    results = {}
    for name, remove in (("primary_426",set()), ("sensitivity_424",omitted)):
        ids = [sid for sid in gold if sid not in remove]
        ref, pred = [gold[sid] for sid in ids], [labels[sid] for sid in ids]
        m = evaluate(ref,pred)
        counts = {}
        for label, stats in m["per_class"].items():
            tp = sum(g == p == label for g,p in zip(ref,pred))
            fp = pred.count(label) - tp
            fn = ref.count(label) - tp
            require((tp,fp,fn) == tuple(stats[k] for k in ("tp","fp","fn")), "confusion counts disagree")
            counts[label] = {k:stats[k] for k in ("tp","fp","fn","f1")}
        results[name] = {"n":len(ids), "correct":sum(g == p for g,p in zip(ref,pred)),
                         "macro_f1":m["macro_f1"], "per_class":counts, "missing":m["failures"]}
    return results


def baseline_german(plan):
    gold = {r.sample_id:r.label for r in pre.data.load_split("test")}
    omitted = {r["sample_id"] for r in plan["near_matches_after_edit"]["german_test"]}
    require(len(omitted) == 2 and len(gold) == 426, "German sensitivity population differs")
    results = {}
    baseline = pre.read(REPORTS / "sun_modality_five_way_v1.json")["methods"]
    for method in ("sun","cfkw","cfrnn","cfcnn"):
        rows = jsonlines(DEV / f"s28_sun_modality_five_way_v1/{method}/local_only/test_predictions.jsonl")
        population(rows, gold)
        require(all(gold[r["sample_id"]] == r["gold"] for r in rows), "German baseline label differs")
        measured = german_metrics({r["sample_id"]:r["predicted"] for r in rows},gold,omitted)
        require(measured["primary_426"]["macro_f1"] == baseline[method]["metrics"]["macro_f1"],method)
        results[method] = measured
    return gold, omitted, results


def old_german(plan):
    gold, omitted, results = baseline_german(plan)
    path = DEV / "sun_modality_es_minimal_v1"
    raw = [r for r in pre.boundary.read_events(path / "E1_full_20261111/events.jsonl") if r["kind"]=="finished"]
    raw += [r for r in pre.boundary.read_events(path / "pilot_20261111/events.jsonl")
            if r["kind"]=="finished" and r["wave"] in ("E1-1","E1-2")]
    population(raw, gold)
    labels = {}
    for r in raw:
        sid = r["sample_id"]
        require(pre.digest(r["raw_content"].encode()) == r["response_sha256"], "E1 response digest")
        labels[sid] = dispatch.canonical(("german","111",sid),"",r)["label"]
        require(labels[sid] == r["label"], "historical German readout differs")
    scores = german_metrics(labels,gold,omitted)
    expected = pre.read(GERMAN / "full_test_results.json")["methods"]["E1"]
    require(all(scores["primary_426"][k] == v for k,v in expected.items()), "historical E1 differs")
    results["historical_E1"] = scores
    return {k:{"primary_426":v["primary_426"]["macro_f1"], "sensitivity_424":v["sensitivity_424"]["macro_f1"]}
            for k,v in results.items()}


def historical(plan, pairs, controls):
    proof = {"run_id":pre.NAME, "requests_sha256":plan["requests_sha256"], "api_calls":0,
             "estg":estg_replay(dict(pairs["estg"])), "german":old_german(plan),
             "gdpr":pre.read(pre.LOCAL / "historical_gdpr_validation.json")}
    require(proof["gdpr"]["passed"] and proof["gdpr"]["signals_checked"] == 6210,"missing GDPR parity")
    paths = [Path(__file__), Path(dispatch.__file__), Path(pre.__file__), Path(dispatch.transport.__file__),
             Path(pre.core.__file__), Path(pre.factorial.__file__), Path(dispatch.gdpr_parser.__file__),
             Path(pre.boundary.__file__), Path(pre.llm_se.__file__), Path(stage2.__file__),
             pre.ROOT / "scripts/score_paper_e1_r19_gdpr.py",
             pre.ROOT / "src/bpc_hybrid/sep_c3_primary_evaluation.py",
             pre.ROOT / "src/bpc_hybrid/d1_schema_adapter.py",
             pre.ROOT / "src/bpc_hybrid/d1_span_canonicalizer.py",
             pre.ROOT / "src/bpc_hybrid/h1_transport.py", pre.ROOT / "src/bpc_hybrid/llm_client.py",
             pre.ROOT / "src/bpc_hybrid/modality_benchmark/metrics.py"]
    paths += [Path(dispatch.transport.base.__file__), Path(pre.isolation.__file__),Path(pre.data.__file__),
              pre.ROOT / "src/bpc_hybrid/stage2_sun_literal_overlap.py"]
    paths += sorted((pre.ROOT / "outputs/evidence/stage3_reproduction_repair_20261012_v1/source_snapshot").rglob("*.py"))
    paths += [PAPER / "04_gdpr_table_III_and_fig3/method" / n for n in ("sun_model.py","local_mpnet_backend_v1.py","evaluation_v2.py")]
    proof["code_sha256"] = {p.relative_to(pre.ROOT).as_posix():pre.digest(p.read_text(encoding="utf-8").encode()) for p in paths}
    proof["control_responses_sha256"] = dispatch.controls_digest(controls)
    proof["passed"] = True
    save(dispatch.DRY,proof)


def score(plan, pairs, bodies, controls):
    texts = {g:dict(rows) for g,rows in pairs.items()}
    jobs = set(bodies) - set(controls)
    events = pre.boundary.read_events(dispatch.JOURNAL)
    hashes = {k:pre.digest(pre.boundary.wire_bytes(bodies[k])) for k in jobs}
    new = dispatch.check_history(events,jobs,texts,hashes)
    require(set(new) == jobs and len(new) == 1359, "complete run required for final scoring")
    started, spent, uncertain = pre.boundary.accounting(events)
    require(len(started)==len(new) and not uncertain, "unsettled billing")
    attempts = {a:[] for a in pre.factorial.ALL_ARMS}
    labels, native = {}, []
    rule_ids = {sid:rid for rid,sid in pre.gdpr_ids().items()}
    for k in bodies:
        group,arm,sid = k
        r = dispatch.canonical(k,texts[group][sid],new[k] if k in new else old_response(controls[k]))
        if group == "estg":
            attempts[arm].append(r)
        elif group == "german":
            labels[sid] = r["label"]
        else:
            # Empty failed extraction yields unknown signals on all applicable checks.
            record = r["record"] or {"sample_id":sid,"source_text":texts[group][sid],"clauses":[]}
            native.append({"requirement_id":rule_ids[sid],"request_status":r["request_status"],"record":record})
    byte_rows = b"".join(pre.encoded(r)+b"\n" for r in native)
    pre.frozen(pre.LOCAL / "local_only/gdpr_native.jsonl",byte_rows)
    gold = pre.read(TABLE1 / "shared/gold_150.json")
    arms = {arm:stage2_metrics(arm,rows,gold) for arm,rows in attempts.items()}
    german_gold, omitted, german = baseline_german(plan)
    german["LLM-SE"] = german_metrics(labels,german_gold,omitted)
    sun = stage2_metrics("Sun",pre.read(TABLE1 / "predictions/Sun.json")["records"],gold)
    save(REPORTS / "paper_e1_r19_v1_scores.json",{
        "run_id":pre.NAME,"scope":"test-informed German analysis; previous frozen paper protocols",
        "system_sha256":plan["revised_system_sha256"],"requests_sha256":plan["requests_sha256"],
        "calls":len(new),"historical_controls":len(controls),"cost_cny":spent,"journal_sha256":events[-1]["event_hash"],
        "table_I":{"Sun":sun,"LLM-SE":arms["111"]},"table_II":arms,
        "gdpr_native_failures":sum(r["request_status"]!="ok" for r in native),"german":german})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("historical","score"))
    args = parser.parse_args()
    plan, pairs, bodies, controls = pre.build()
    require(plan == pre.read(pre.REPORT),"plan changed")
    if args.mode == "historical":
        historical(plan,pairs,controls)
    else:
        score(plan,pairs,bodies,controls)
    print(f"{args.mode}: complete")
