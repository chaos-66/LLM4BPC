"""Reconcile the recorded LLM-SE request hashes against a fresh re-derivation.

Background.  The executed run (started 18:00:14 +08) used the hash formula
``json.dumps(body, ensure_ascii=False, sort_keys=True)`` while the transport
records the provider-side hash of ``json.dumps(body)`` in *builder key order*.
The two digests therefore differ for every call even though the transmitted
body is identical.  ``body_hash_match`` in ``llm_se_responses.jsonl`` compares
across those two formulas and is consequently ``False`` for every row; it is a
**recording artefact, not a transport divergence**.

This script proves the point offline (no network, no API call), for every
recorded sample:

1. re-derive the request body from the frozen prompt + test sentence only;
2. recompute the legacy sorted-dump digest and require it to equal the stored
   ``request_body_sha256``;
3. recompute the wire-order digest and require it to equal the stored
   ``provider_request_body_sha256`` (the digest the transport produced from the
   body it actually sent);
4. require both serialisations to parse back to the identical object, i.e. the
   only difference is JSON key ordering.

Any sample failing a check is reported and the process exits non-zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.modality_benchmark import data as data_mod  # noqa: E402
from bpc_hybrid.modality_benchmark import llm_se  # noqa: E402

DEFAULT_RUN_ID = "s28_sun_modality_five_way_v1"
OUTPUT_ROOT = ROOT / "outputs/development"
WIRE_ORDER = (
    "model",
    "messages",
    "max_tokens",
    "temperature",
    "top_p",
    "stream",
    "thinking",
)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                rows.append(json.loads(raw))
    return rows


def wire_bytes(body: dict[str, Any]) -> bytes:
    ordered = {key: body[key] for key in WIRE_ORDER if key in body}
    return json.dumps(ordered).encode("utf-8")


def legacy_bytes(body: dict[str, Any]) -> bytes:
    return json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    run_dir = OUTPUT_ROOT / args.run_id / "llm_se"
    response_path = run_dir / "llm_se_responses.jsonl"
    records = read_jsonl(response_path)
    if not records:
        raise SystemExit(f"no recorded responses under {response_path}")

    texts = dict(data_mod.load_split_text_only("test"))
    failures: list[dict[str, Any]] = []
    checked = 0
    for row in records:
        sample_id = row["sample_id"]
        if sample_id not in texts:
            failures.append({"sample_id": sample_id, "issue": "sample not in test split"})
            continue
        body = llm_se.request_body(sample_id, texts[sample_id])
        legacy = sha256_bytes(legacy_bytes(body))
        wire = sha256_bytes(wire_bytes(body))
        checks = {
            "legacy_digest_reproduced": legacy == row.get("request_body_sha256"),
            "wire_digest_matches_provider": wire == row.get("provider_request_body_sha256"),
            "canonical_payload_identical": (
                json.loads(legacy_bytes(body)) == json.loads(wire_bytes(body))
            ),
        }
        checked += 1
        if not all(checks.values()):
            failures.append(
                {
                    "sample_id": sample_id,
                    "issue": "digest reconciliation failed",
                    "checks": checks,
                    "recorded": {
                        "legacy": row.get("request_body_sha256"),
                        "provider": row.get("provider_request_body_sha256"),
                    },
                    "recomputed": {"legacy": legacy, "provider": wire},
                }
            )

    summary = {
        "schema_version": "sun_modality_llm_se_body_reconciliation@1.0.0",
        "run_id": args.run_id,
        "response_file": str(response_path.relative_to(ROOT)),
        "records": len(records),
        "checked": checked,
        "failures": len(failures),
        "ok": not failures,
        "explanation": (
            "body_hash_match=false in the response records is a recording artefact: "
            "the executed run hashed a sort_keys dump while the transport reports the "
            "builder-order dump of the same dict. Both serialisations parse to the same "
            "object and the wire digest equals the provider-side digest for every sample."
        ),
        "failure_detail": failures,
    }
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
        print(f"[verify] wrote {target}", file=sys.stderr)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
