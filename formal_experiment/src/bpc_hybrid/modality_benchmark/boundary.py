"""Offline-only, single-change prompt branch; never reads credentials or Gold."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import llm_se

ROOT = llm_se.PROJECT_ROOT
GUIDANCE = ROOT / "prompts/sun_compat/modality_boundary_v1/boundary_guidance.md"
CONTRACT = ROOT / "configs/supplement/sun_modality_boundary_v1.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if digest(GUIDANCE.read_bytes()) != contract["guidance_sha256"]:
        raise ValueError("boundary guidance changed after freeze")
    if contract["parent_prompt_sha256"] != llm_se.PROMPT_SHA256:
        raise ValueError("parent prompt binding changed")
    return contract


def request_body(sample_id: str, text: str) -> dict[str, Any]:
    read_contract()
    body = llm_se.request_body(sample_id, text)
    body["messages"][0]["content"] += "\n\n" + GUIDANCE.read_text(encoding="utf-8").strip()
    return body


def wire_bytes(body: dict[str, Any]) -> bytes:
    order = ("model", "messages", "max_tokens", "temperature", "top_p", "stream", "thinking")
    return json.dumps({key: body[key] for key in order if key in body}).encode("utf-8")


def reserve_cost(body: dict[str, Any], rate: dict[str, float]) -> float:
    # One token per UTF-8 byte plus a generous envelope allowance, all cache
    # misses, and the COMPLETE max_tokens allowance; no optimistic 1200-token cap.
    input_bound = len(wire_bytes(body)) + 1024
    return (input_bound * rate["input_cache_miss"]
            + body["max_tokens"] * rate["output"]) / 1_000_000


def append_event(path: Path, event: dict[str, Any], previous: str) -> str:
    event = dict(event, previous_hash=previous)
    hashed = digest(json.dumps(event, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    event["event_hash"] = hashed
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        import os
        os.fsync(handle.fileno())
    return hashed


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events, previous, started, finished = [], "", set(), set()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        actual = row.pop("event_hash")
        expected = digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        if actual != expected or row["previous_hash"] != previous:
            raise ValueError("journal hash chain mismatch")
        sid = row["sample_id"]
        if row["kind"] == "started":
            if sid in started:
                raise ValueError("duplicate request; retries are forbidden")
            started.add(sid)
        elif row["kind"] == "finished":
            if sid not in started or sid in finished:
                raise ValueError("unmatched/duplicate completion")
            finished.add(sid)
        else:
            raise ValueError("unknown journal event")
        row["event_hash"] = actual
        events.append(row)
        previous = actual
    return events


def accounting(events: list[dict[str, Any]]) -> tuple[set[str], float, float]:
    starts = {x["sample_id"]: x for x in events if x["kind"] == "started"}
    finishes = {x["sample_id"]: x for x in events if x["kind"] == "finished"}
    spent = sum(x["cost_cny"] for x in finishes.values())
    uncertain = sum(x["reserved_cny"] for sid, x in starts.items()
                    if sid not in finishes or not finishes[sid]["usage_verified"])
    return set(starts), spent, uncertain
