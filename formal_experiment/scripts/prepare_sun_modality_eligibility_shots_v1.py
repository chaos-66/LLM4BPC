"""Build the reviewer + four train demonstrations prompt, offline."""
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.datasets.sun_modality_importer import normalize_for_dedup
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, review_prompt
from prepare_sun_modality_fewshot_v1 import write_frozen

MANIFEST = ROOT / "prompts/sun_compat/modality_eligibility_shots_v1/selection_manifest.json"
LOCAL = ROOT / "outputs/development/sun_modality_eligibility_shots_v1"
REPORT = ROOT / "outputs/reports/sun_modality_eligibility_shots_v1_preflight.json"


def tokens(text):
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())


def near_match(left, right):
    """Flag a small edit or an almost verbatim excerpt, including an embedded sentence."""
    words = SequenceMatcher(None, left, right, autojunk=False)
    if words.ratio() >= 0.80:
        return True
    shorter = min(len(left), len(right))
    if shorter >= 8 and words.find_longest_match().size >= 0.85 * shorter:
        return True
    chars = SequenceMatcher(None, " ".join(left), " ".join(right), autojunk=False)
    return chars.quick_ratio() >= 0.88 and chars.ratio() >= 0.88


def resolve_examples(train, specs, inherited_ids):
    lookup = {row.sample_id: row for row in train}
    ids = [spec["sample_id"] for spec in specs]
    if len(ids) != 4 or len(set(ids)) != 4 or set(ids) & inherited_ids:
        raise ValueError("expected four distinct additions outside the original 18")
    if [spec["label"] for spec in specs] != ["definition", "permission"] * 2:
        raise ValueError("expected two definition/permission pairs")
    selected = []
    for spec in specs:
        row = lookup.get(spec["sample_id"])
        if row is None or row.label != spec["label"] or boundary.digest(row.text.encode()) != spec["text_sha256"]:
            raise ValueError("training membership, label or text hash mismatch")
        selected.append(row)
    if len({normalize_for_dedup(row.text) for row in selected}) != len(selected):
        raise ValueError("duplicate training text")
    return selected


def check_isolation(selected, held_out):
    signatures = [(r.sample_id, normalize_for_dedup(r.text), tokens(r.text)) for r in selected]
    for sid, text in held_out:
        normalized, words = normalize_for_dedup(text), tokens(text)
        for selected_id, selected_text, selected_words in signatures:
            if sid == selected_id or normalized == selected_text or near_match(selected_words, words):
                raise ValueError(f"held-out overlap for fixed training example {selected_id}")


def build():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    train_spec = data.EXPECTED["train"]
    if manifest["source_split"] != "train" or data.sha256_file(train_spec["path"]) != manifest["train_sha256"]:
        raise ValueError("training source differs from manifest")
    original_block, original_manifest = fewshot.load_demonstrations()
    inherited = {r["sample_id"] for r in original_manifest["selections"]}
    selected = resolve_examples(data.load_split("train"), manifest["examples"], inherited)
    counts = {}
    for name in ("dev", "test"):
        texts = data.load_split_text_only(name)
        check_isolation(selected, texts)
        counts[name] = len(texts)

    # The sentinel only instantiates the frozen request template; it never enters the system prompt.
    parent = review_prompt.request_body("local_preview", "Local preview.", block=original_block)
    system = parent["messages"][0]["content"]
    if boundary.digest(system.encode()) != manifest["parent_system_sha256"]:
        raise ValueError("reviewer prompt drift")
    lines = ["Additional German training demonstrations (sentence-level corpus labels).", ""]
    for i, row in enumerate(selected, start=len(inherited) + 1):
        lines.append(f'{i}. "{row.text}" -> {row.label}')
    block = "\n".join(lines)
    composed = system + "\n\n" + block
    report = {
        "id": manifest["id"], "status": "offline_prompt_prepared", "api_calls": 0,
        "performance_metrics": None, "source_split": "train",
        "manifest_sha256_lf": boundary.digest(MANIFEST.read_text(encoding="utf-8").encode()),
        "split_sha256": {s: spec["sha256"] for s, spec in data.EXPECTED.items()},
        "original_train_examples": len(inherited), "new_train_examples": len(selected),
        "all_examples_train_total": len(inherited) + len(selected),
        "new_train_vs_held_out_comparisons": {s: n * len(selected) for s, n in counts.items()},
        "original_and_new_exact_id_or_normalized_text_hits": 0,
        "new_near_duplicate_hits": 0, "held_out_labels_read_by_selector": False,
        "parent_system_sha256": manifest["parent_system_sha256"],
        "new_block_sha256": boundary.digest(block.encode()),
        "composed_system_sha256": boundary.digest(composed.encode()),
        "scope": "Design informed by previously examined held-out errors; no new performance result.",
    }
    return composed, block, report


def main():
    composed, block, report = build()
    write_frozen(LOCAL / "composed_system_prompt.txt", (composed + "\n").encode())
    write_frozen(LOCAL / "added_examples.txt", (block + "\n").encode())
    write_frozen(REPORT, (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
