"""Prepare two small E-only / S-only changes to the original 22-shot, offline."""
import argparse
import json
from pathlib import Path

import prepare_sun_modality_eligibility_shots_v1 as base
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se

ROOT = base.ROOT
CHANGES = ROOT / "prompts/sun_compat/modality_es_minimal_v1/changes.json"
LOCAL = ROOT / "outputs/development/sun_modality_es_minimal_v1"
REPORT = ROOT / "outputs/reports/sun_modality_es_minimal_v1_preflight.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def replace_once(text, before, after):
    if not before or before == after or text.count(before) != 1:
        raise ValueError("prompt edit must match exactly one distinct passage")
    return text.replace(before, after, 1)


def resolve_train_row(train, spec):
    row = train.get(spec["sample_id"])
    if (row is None or row.label != spec["label"]
            or boundary.digest(row.text.encode()) != spec["text_sha256"]):
        raise ValueError("training membership, original label or text hash differs")
    return row


def request_body(system, sample_id, source_text):
    """Use the existing output, user input and sampling; only system text varies."""
    body = llm_se.request_body(sample_id, source_text)
    body["messages"][0]["content"] = system
    return body


def build():
    changes = read(CHANGES)
    baseline, _, baseline_report = base.build()
    if (baseline_report != read(base.REPORT)
            or boundary.digest(baseline.encode()) != changes["base_system_sha256"]):
        raise ValueError("original 22-shot differs from the frozen control")
    if data.sha256_file(data.EXPECTED["train"]["path"]) != changes["train_sha256"]:
        raise ValueError("train source differs")
    train = {r.sample_id: r for r in data.load_split("train")}
    _, original = fewshot.load_demonstrations()
    specs = original["selections"] + read(base.MANIFEST)["examples"]
    ids = [s["sample_id"] for s in specs]
    edit = changes["E1"]
    old = resolve_train_row(train, edit["old"])
    new = resolve_train_row(train, edit["new"])
    if (len(ids) != 22 or edit["position"] != 15 or ids[14] != old.sample_id
            or new.sample_id in ids
            or old.label != "definition" or new.label != "definition"):
        raise ValueError("expected one definition replacement at position 15")
    comparison_counts = {}
    for split in ("dev", "test"):
        held_out = data.load_split_text_only(split)
        base.check_isolation([new], held_out)
        comparison_counts[split] = len(held_out)
    before = f'15. "{old.text}" -> {old.label}'
    after = f'15. "{new.text}" -> {new.label}'
    systems = {"E1": replace_once(baseline, before, after),
               "S1": replace_once(baseline, changes["S1"]["before"], changes["S1"]["after"])}
    template = request_body(baseline, "{sample_id}", "{source_text}")
    unchanged_request = {k: v for k, v in template.items() if k != "messages"}
    unchanged_request["user_message"] = template["messages"][1]
    sources = [CHANGES, Path(__file__), ROOT / "tests/test_modality_es_minimal_v1.py",
               ROOT / "src/bpc_hybrid/modality_benchmark/llm_se.py",
               ROOT / "src/bpc_hybrid/modality_benchmark/metrics.py",
               ROOT / "configs/schemas/stage2_prediction.schema.json"]
    report = {
        "suite_id": changes["suite_id"], "status": "offline_prepared_not_executed",
        "api_calls": 0, "api_authorized": False, "performance_metrics": None,
        "base_system_sha256": changes["base_system_sha256"],
        "baseline_preflight_sha256": boundary.digest(base.REPORT.read_bytes()),
        "source_sha256_lf_utf8": {p.relative_to(ROOT).as_posix(): boundary.digest(p.read_text(encoding="utf-8").encode()) for p in sources},
        "train_sha256": changes["train_sha256"],
        "new_example_vs_held_out_comparisons": comparison_counts,
        "new_exact_or_near_duplicate_hits": 0,
        "retained_21_examples": "unchanged; reuse original exact ID/text isolation, not a new near-duplicate claim",
        "held_out_labels_read": False, "unchanged_request_fields": unchanged_request,
        "readout": "unchanged llm_se.extract_modality_label; coordinate errors do not veto modality",
        "variants": {},
        "scope": "Design informed by previously inspected errors; no new scores, dispatched requests or model calls. E1 and S1 are separate, not combined.",
    }
    for variant, system in systems.items():
        variant_ids = list(ids)
        if variant == "E1":
            variant_ids[14] = new.sample_id
        labels = [train[sid].label for sid in variant_ids]
        report["variants"][variant] = {
            "system_sha256": boundary.digest(system.encode()),
            "system_characters": len(system), "train_example_count": len(variant_ids),
            "train_example_ids": variant_ids,
            "class_totals": {label: labels.count(label) for label in sorted(set(labels))},
            "local_system_path": (LOCAL / f"{variant}_system_prompt.txt").relative_to(ROOT).as_posix(),
        }
    return baseline, systems, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare saved offline artifacts without writing")
    args = parser.parse_args()
    _, systems, report = build()
    artifacts = {REPORT: (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()}
    for variant, system in systems.items():
        artifacts[LOCAL / f"{variant}_system_prompt.txt"] = (system + "\n").encode()
        artifacts[LOCAL / f"{variant}_request_template.json"] = (
            json.dumps(request_body(system, "{sample_id}", "{source_text}"), ensure_ascii=False, indent=2) + "\n").encode()
    for path, raw in artifacts.items():
        if args.check:
            if not path.exists() or path.read_bytes() != raw:
                raise ValueError("offline artifact differs: " + str(path))
        else:
            write_frozen(path, raw)
    print(json.dumps({"variants": list(systems), "api_calls": 0,
                      "checked" if args.check else "prepared": True,
                      "new_example_isolation_comparisons": sum(report["new_example_vs_held_out_comparisons"].values())}))


if __name__ == "__main__":
    main()
