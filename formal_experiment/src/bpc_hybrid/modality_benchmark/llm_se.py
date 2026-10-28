"""LLM-SE arm for the Sun modality supplement.

Reuses the **frozen** paper prompt and sampling policy of the EStG-150
LLM-SE arm (`direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`, schema
`stage2_prediction.schema.json@1.0.0`), and takes the sentence modality
label from the produced record exactly the way the project evaluator does
(`_pred_modality_label`: first clause with a non-empty modality label).

Deviations from the EStG-150 run are recorded, not hidden:

* the target text is the **German** Sun/Michel sentence (the EStG-150 arm
  used the approved English text), because every arm in this supplement
  must see the same German original;
* the model is the frozen alias `deepseek-v4-pro` (documented release
  DeepSeek-V4-Pro-0813), temperature 0, top_p 1, max_tokens 4096,
  thinking disabled, no retry, one request per test sample;
* the budget is a hard CNY cap with per-call reservation, priced with the
  official peak/off-peak table in force at run time.

No Gold label is read by this module.  Parsing failures are recorded as
``no prediction`` and stay in the evaluation denominator.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from bpc_hybrid.prompt_loader import load_prompt

from .metrics import LABELS

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROMPT_NAME = "direct_llm_sun_record_prompt_v6_d1r1_2026_08_05"
PROMPT_PATH = PROJECT_ROOT / "prompts/sun_compat" / f"{PROMPT_NAME}.md"
PROMPT_SHA256 = (
    "3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478c34ad04621c0ede895"
)
MODEL_ALIAS = "deepseek-v4-pro"
DOCUMENTED_RELEASE = "DeepSeek-V4-Pro-0813"
MAX_OUTPUT_TOKENS = 4096

BEIJING = timezone(timedelta(hours=8))

# Official DeepSeek price table, CNY per million tokens, verified
# 2026-10-28 from https://api-docs.deepseek.com/zh-cn/quick_start/pricing/
PRICE_CNY_PER_MILLION: dict[str, dict[str, float]] = {
    "peak": {
        "input_cache_hit": 0.30,
        "input_cache_miss": 9.0,
        "output": 27.0,
    },
    "off_peak": {
        "input_cache_hit": 0.15,
        "input_cache_miss": 4.5,
        "output": 13.5,
    },
}
PRICE_SOURCE_URL = "https://api-docs.deepseek.com/zh-cn/quick_start/pricing/"
PRICE_VERIFIED_AT = "2026-10-28T17:20:00+08:00"


class BudgetExceeded(RuntimeError):
    """Raised before a send that would break the hard CNY cap."""


class PromptContractError(ValueError):
    """Raised when the frozen prompt does not match its declared hash."""


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_frozen_prompt() -> tuple[Any, str, str]:
    """Return (loaded prompt, system prompt, few-shot block) after hash check."""
    from .data import sha256_file

    if not PROMPT_PATH.exists():
        raise PromptContractError(f"missing frozen prompt: {PROMPT_PATH}")
    digest = sha256_file(PROMPT_PATH)
    if digest != PROMPT_SHA256:
        raise PromptContractError(
            f"frozen prompt hash mismatch: {digest} != {PROMPT_SHA256}"
        )
    prompt = load_prompt(PROMPT_NAME)
    if not prompt.system_prompt or not prompt.user_prompt_template:
        raise PromptContractError("frozen prompt is missing system/user sections")
    raw = prompt.raw_text
    start = raw.find("## Examples")
    end = raw.find("## Notes", start)
    if start < 0 or end < 0:
        raise PromptContractError("frozen prompt has no Examples/Notes section")
    few_shot = raw[start:end].strip()
    return prompt, prompt.system_prompt, few_shot


def render(sample_id: str, source_text: str) -> tuple[str, str]:
    prompt, system, few_shot = load_frozen_prompt()
    user = prompt.user_prompt_template.format(
        sample_id=sample_id,
        source_id=sample_id,
        source_text=source_text,
        few_shot_block=few_shot,
    )
    return system, user


def request_body(sample_id: str, source_text: str) -> dict[str, Any]:
    system, user = render(sample_id, source_text)
    return {
        "model": MODEL_ALIAS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "stream": False,
        "thinking": {"type": "disabled"},
    }


def estimate_input_tokens(body: Mapping[str, Any]) -> int:
    """Project policy: UTF-8 request bytes / 3, rounded up (no tokenizer)."""
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return math.ceil(len(raw) / 3)


def is_peak(dt: datetime, holidays: Sequence[str] = ()) -> bool:
    local = dt.astimezone(BEIJING)
    if local.strftime("%Y-%m-%d") in set(holidays):
        return False
    if local.weekday() >= 5:
        return False
    minutes = local.hour * 60 + local.minute
    return (9 * 60 <= minutes < 12 * 60) or (14 * 60 <= minutes < 18 * 60)


def rate_for(dt: datetime, holidays: Sequence[str] = ()) -> tuple[str, dict[str, float]]:
    window = "peak" if is_peak(dt, holidays) else "off_peak"
    return window, PRICE_CNY_PER_MILLION[window]


def cost_cny(usage: Mapping[str, Any], rate: Mapping[str, float]) -> float:
    """Actual cost from provider usage; missing cache split -> cache-miss."""
    prompt_tokens = float(usage.get("prompt_tokens") or 0)
    completion_tokens = float(usage.get("completion_tokens") or 0)
    hit = float(usage.get("prompt_cache_hit_tokens") or 0)
    miss_raw = usage.get("prompt_cache_miss_tokens")
    miss = float(miss_raw) if miss_raw is not None else max(prompt_tokens - hit, 0.0)
    return (
        hit * rate["input_cache_hit"]
        + miss * rate["input_cache_miss"]
        + completion_tokens * rate["output"]
    ) / 1_000_000.0


@dataclass
class CostGate:
    """Hard CNY cap with per-send reservation.

    ``spent_cny`` only grows from real provider usage.  ``reserved_cny``
    holds the worst-case reservation of in-flight sends, which for this
    single-threaded runner is released immediately after each response.
    """

    cap_cny: float
    reserve_output_tokens: int = 1200
    spent_cny: float = 0.0
    reserved_cny: float = 0.0
    calls: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def reserve(self, projected_input_tokens: int, rate: Mapping[str, float], now: datetime) -> float:
        reserve = (
            projected_input_tokens * rate["input_cache_miss"]
            + self.reserve_output_tokens * rate["output"]
        ) / 1_000_000.0
        if self.spent_cny + self.reserved_cny + reserve > self.cap_cny + 1e-12:
            raise BudgetExceeded(
                "budget cap would be exceeded before send: "
                f"spent={self.spent_cny:.4f} reserved={self.reserved_cny:.4f} "
                f"request={reserve:.4f} cap={self.cap_cny:.2f}"
            )
        self.reserved_cny += reserve
        return reserve

    def settle(self, usage: Mapping[str, Any], rate: Mapping[str, float], reservation: float) -> float:
        self.reserved_cny = max(self.reserved_cny - reservation, 0.0)
        actual = cost_cny(usage, rate)
        self.spent_cny += actual
        return actual


def _extract_json_object(content: str) -> dict[str, Any] | None:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def extract_modality_label(content: str) -> dict[str, Any]:
    """Take the first non-empty clause modality label (project convention)."""
    record = _extract_json_object(content)
    if record is None:
        return {"label": None, "status": "invalid_json", "clauses": 0}
    clauses = record.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        return {"label": None, "status": "no_clauses", "clauses": 0}
    for clause in clauses:
        if not isinstance(clause, dict):
            continue
        modality = clause.get("modality")
        label = modality.get("label") if isinstance(modality, dict) else None
        if isinstance(label, str) and label:
            if label not in LABELS:
                return {
                    "label": None,
                    "status": "invalid_label",
                    "clauses": len(clauses),
                    "raw_label": label,
                }
            return {"label": label, "status": "ok", "clauses": len(clauses)}
    return {"label": None, "status": "no_label", "clauses": len(clauses)}


def prompt_overlap_report(test_texts: Sequence[str]) -> dict[str, Any]:
    """Exact and token-normalised overlap of prompt examples with the test set."""

    def norm(text: str) -> str:
        return " ".join("".join(ch if ch.isalnum() else " " for ch in text.lower()).split())

    prompt, _, few_shot = load_frozen_prompt()
    example_inputs = [
        block.split("Input:", 1)[1].split("\n", 1)[0].strip().strip('"')
        for block in few_shot.split("Example ")[1:]
        if "Input:" in block
    ]
    test_norm = {norm(text) for text in test_texts}
    normalized_hits = [ex for ex in example_inputs if norm(ex) in test_norm]
    raw_hits = [ex for ex in example_inputs if ex.strip() in set(test_texts)]
    return {
        "prompt_path": PROMPT_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "prompt_sha256": PROMPT_SHA256,
        "examples_found": len(example_inputs),
        "examples": example_inputs,
        "raw_text_overlap": len(raw_hits),
        "normalized_text_overlap": len(normalized_hits),
        "note": (
            "few-shot examples are synthetic English sentences; the test "
            "population is German, so a lexical overlap of 0 is expected and "
            "was verified rather than assumed"
        ),
    }
