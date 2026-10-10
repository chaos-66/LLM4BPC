# -*- coding: utf-8 -*-
"""Generate the minimal final human-approval packet for Stage-3 bindings.

Only fields that still require a substantive human judgment are included.
Every item shows the relevant sentence/candidates/target context and offers
simple ACCEPT / CHANGE TO <id> / N/A options.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.stage1_process import load_stage1_contract, parse_bpmn_file  # noqa: E402
from bpc_hybrid.stage3_grounding.automatic_rule_process_grounding_v1 import (  # noqa: E402
    DEFAULT_DIRECT_PREDICTIONS,
    DEFAULT_STAGE2_INPUT,
    load_direct_llm_rule_index,
)

REFERENCE = ROOT / "data/development/stage3_synth/stage3_binding_reference_v1.json"
HUMAN = ROOT / "data/development/stage3_synth/stage3_binding_human_decisions_v1.json"
RESOLVED = ROOT / "data/development/stage3_synth/stage3_binding_resolved_reference_v1.json"
BENCHMARK = ROOT / "data/development/stage3_synth/stage3_paired_benchmark_v1.json"
CONTRACT = ROOT / "configs/stage1_structural_s11_s14.json"
OUT = ROOT / "outputs/reports/stage3_binding_final_human_approval_packet_v1.md"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _lane_name(record: dict[str, Any], lane_id: str | None) -> str:
    for lane in record.get("lanes") or []:
        if str(lane.get("id")) == str(lane_id):
            return str(lane.get("name") or "")
    for pool in record.get("pools") or []:
        if str(pool.get("id")) == str(lane_id):
            return str(pool.get("name") or "")
    return ""


def _neighbors(record: dict[str, Any], activity_id: str
               ) -> tuple[list[str], list[str]]:
    edges = (record.get("control_flow") or {}).get("direct_edges") or []
    preds = [str(e.get("source_ref")) for e in edges
             if str(e.get("target_ref")) == str(activity_id)]
    succs = [str(e.get("target_ref")) for e in edges
             if str(e.get("source_ref")) == str(activity_id)]
    names = {str(a["id"]): str(a.get("name") or "") for a in record.get("activities") or []}
    return ([f"{x} ({names.get(x, '')})" for x in preds],
            [f"{x} ({names.get(x, '')})" for x in succs])


def _ordering(record: dict[str, Any], a: str, b: str) -> str:
    edges = {(str(e.get("source_ref")), str(e.get("target_ref")))
             for e in (record.get("control_flow") or {}).get("direct_edges") or []}
    reach = {(str(e.get("source_ref")), str(e.get("target_ref")))
             for e in (record.get("control_flow") or {}).get("reachable_pairs") or []}
    fwd = (a, b) in edges or (a, b) in reach
    bwd = (b, a) in edges or (b, a) in reach
    if fwd and not bwd:
        return "forward only"
    if bwd and not fwd:
        return "backward only"
    if fwd and bwd:
        return "cyclic/both"
    return "none"


def _fmt_action_list(items: list[dict[str, Any]]) -> list[str]:
    lines = []
    for item in items:
        lines.append(f"* `{item.get('rule_action_id')}`: \"{item.get('text')}\" "
                     f"(modality={item.get('modality')}, sample={item.get('sample_id')})")
    return lines


def _clean(text: Any) -> str:
    return " ".join(str(text or "").split())


def main() -> int:
    reference = {str(r["pair_id"]): r for r in _load(REFERENCE)["records"]}
    human = _load(HUMAN)["records"]
    resolved = {str(r["pair_id"]): r for r in _load(RESOLVED)["records"]}
    benchmark = _load(BENCHMARK)
    controls = {
        str(i["pair_id"]): i for i in benchmark["items"]
        if i.get("role") == "control"
    }
    variants = {
        str(i["pair_id"]): i for i in benchmark["items"]
        if i.get("role") == "variant"
    }
    contract = load_stage1_contract(CONTRACT)
    rule_index = load_direct_llm_rule_index(
        DEFAULT_DIRECT_PREDICTIONS, DEFAULT_STAGE2_INPUT
    )
    cache: dict[str, dict[str, Any]] = {}

    def parsed(rel_path: str) -> dict[str, Any]:
        if rel_path not in cache:
            cache[rel_path] = parse_bpmn_file(ROOT / rel_path, contract=contract)
        return cache[rel_path]

    unresolved: list[str] = []
    for pair_id, ref in sorted(reference.items()):
        action = ref.get("action_binding") or {}
        actor = ref.get("actor_binding") or {}
        order = ref.get("order_binding") or {}
        needs = (
            not action.get("human_approved")
            or not actor.get("human_approved")
            or (ref.get("target_violation_type") == "out_of_order"
                and not order.get("human_approved"))
        )
        if needs:
            unresolved.append(pair_id)

    lines: list[str] = [
        "# Stage 3 binding: final human approval packet v1",
        "",
        "This packet contains only items that still require substantive human "
        "judgment. Mechanical conversions and human-confirmed fields are not "
        "included. For each option below, choose exactly one simple action:",
        "",
        "- `ACCEPT` = accept the AI recommendation shown;",
        "- `CHANGE TO <id>` = replace it with the id you specify;",
        "- `N/A` = no legal binding is applicable.",
        "",
        f"Pairs requiring approval: {len(unresolved)} / 30.",
        "",
        "---",
        "",
    ]

    for pair_id in unresolved:
        ref = reference[pair_id]
        control_item = controls[pair_id]
        variant_item = variants.get(pair_id) or {}
        control = parsed(control_item["bpmn_path"])
        variant = parsed(variant_item.get("bpmn_path", control_item["bpmn_path"]))
        target_id = str(ref.get("target_activity_id") or "")
        target_name = next((str(a.get("name") or "") for a in control.get("activities") or []
                            if str(a.get("id")) == target_id), "")
        lane_id = None
        for activity in control.get("activities") or []:
            if str(activity.get("id")) == target_id:
                lane_id = (activity.get("lane_ids") or [None])[0]
        preds, succs = _neighbors(control, target_id)
        human_record = human.get(pair_id) or {}
        regulation_text = _clean(
            (control_item.get("grounding") or {}).get("rule_action_text") or "")
        actions = rule_index.get(str(ref.get("rule_id")), [])
        flat_actions = [a for rec in actions for a in rec.get("actions") or []]
        flat_actors = []
        seen_actors: set[str] = set()
        for rec in actions:
            for actor in rec.get("actors") or []:
                if actor.get("rule_actor_id") not in seen_actors:
                    seen_actors.add(actor.get("rule_actor_id"))
                    flat_actors.append(actor)

        lines += [
            f"## Pair `{pair_id}`",
            "",
            f"- rule: `{ref.get('rule_id')}`",
            f"- process: `{ref.get('process_id')}`",
            f"- target violation type: `{ref.get('target_violation_type')}`",
            f"- regulation text: \"{regulation_text or 'not available'}\"",
            f"- target BPMN activity: `{target_id}` \"{target_name}\""
            f" (lane `{lane_id}` \"{_lane_name(control, lane_id)}\")",
            f"- predecessors: {', '.join(preds) if preds else 'none'}",
            f"- successors: {', '.join(succs) if succs else 'none'}",
            "",
        ]

        if not (ref.get("action_binding") or {}).get("human_approved"):
            action = ref.get("action_binding") or {}
            action_evidence = action.get("evidence") or []
            action_evidence_text = (
                _clean(action_evidence[0].get("text"))
                if action_evidence and isinstance(action_evidence[0], dict)
                else "not recorded"
            )
            lines += [
                "### Action binding (unresolved)",
                "",
                "Relevant LLM-SE Rule Record action candidates:",
                "",
                *_fmt_action_list(flat_actions),
                "",
                f"**AI recommendation:** `{action.get('rule_action_id') or 'N/A'}` "
                f"(status `{action.get('status')}`, authority `{action.get('authority')}`).",
                "",
                f"- candidate span evidence: \"{action_evidence_text}\"",
                f"- confidence: not recorded (status/evidence-based AI resolution)",
                "",
                f"Evidence/reason: {action.get('reason') or 'n/a'}",
                "",
                "Options: `ACCEPT` / `CHANGE TO <rule_action_id>` / `N/A`",
                "",
            ]

        if not (ref.get("actor_binding") or {}).get("human_approved"):
            actor = ref.get("actor_binding") or {}
            actor_evidence = actor.get("evidence") or []
            actor_evidence_text = (
                _clean(actor_evidence[0].get("text"))
                if actor_evidence and isinstance(actor_evidence[0], dict)
                else "not recorded"
            )
            right_holder = actor.get("right_holder_reference") or {}
            lines += [
                "### Actor / lane binding (unresolved)",
                "",
                "Relevant LLM-SE Rule Record actor candidates:",
                "",
            ]
            for item in flat_actors:
                lines.append(f"* `{item.get('rule_actor_id')}`: \"{item.get('text')}\" "
                             f"(sample={item.get('sample_id')})")
            lines += [
                "",
                f"- candidate actor span evidence: \"{actor_evidence_text}\"",
                f"- right-holder reference: `{right_holder.get('id') or 'N/A'}` "
                f"\"{_clean(right_holder.get('text')) or 'N/A'}\"",
                f"- confidence: not recorded (status/evidence-based AI resolution)",
                "",
                f"**AI recommendation:** rule actor "
                f"`{actor.get('rule_actor_id') or 'N/A'}`; process executor "
                f"`{actor.get('executor_name') or 'N/A'}`; expected lane "
                f"`{actor.get('expected_lane_id')}` "
                f"\"{_lane_name(control, actor.get('expected_lane_id'))}\" "
                f"(status `{actor.get('status')}`).",
                "",
                f"Evidence/reason: {actor.get('reason') or 'n/a'}",
                "",
                "Options: `ACCEPT` / `CHANGE TO <rule_actor_id>` / `CHANGE LANE TO <lane_id>` / `N/A`",
                "",
            ]

        if (ref.get("target_violation_type") == "out_of_order"
                and not (ref.get("order_binding") or {}).get("human_approved")):
            order = ref.get("order_binding") or {}
            order_pair = (control_item.get("grounding") or {}).get("order_pair") or []
            process_labels = []
            for activity_id in order_pair:
                label = next((str(a.get("name") or "") for a in control.get("activities") or []
                              if str(a.get("id")) == str(activity_id)), "")
                process_labels.append(f"`{activity_id}` \"{label}\"")
            control_order = (
                _ordering(control, order_pair[0], order_pair[1])
                if len(order_pair) == 2 else "none"
            )
            variant_order = (
                _ordering(variant, order_pair[0], order_pair[1])
                if len(order_pair) == 2 else "none"
            )
            order_evidence = order.get("evidence") or []
            order_evidence_texts = [
                _clean(e.get("text")) for e in order_evidence
                if isinstance(e, dict) and e.get("text")
            ]
            process_order = human_record.get("process_order") or {}
            order_confidence = process_order.get("confidence")
            lines += [
                "### Rule-side order relation (unresolved)",
                "",
                f"- benchmark process pair: {', '.join(process_labels) if process_labels else 'none'}",
                f"- control BPMN order: `{control_order}`",
                f"- variant BPMN order: `{variant_order}`",
                f"- AI recommendation: `N/A` (`{order.get('status')}`)",
                f"- confidence: {order_confidence if order_confidence is not None else 'not recorded'}",
                "",
            ]
            for evidence_text in order_evidence_texts[:3]:
                lines.append(f"- regulation/order evidence: \"{evidence_text}\"")
            lines += [
                "",
                f"Evidence/reason: {order.get('reason') or 'n/a'}",
                "",
                "Options: `ACCEPT N/A` / `DEFINE before=<rule_action_id> after=<rule_action_id>`",
                "",
            ]

        lines += ["---", ""]

    lines += [
        "## Approval result format",
        "",
        "Return one line per pair, for example:",
        "",
        "```text",
        "syn_incorrect_actor_03: action=N/A; actor=ACCEPT",
        "syn_out_of_order_01: order=ACCEPT N/A",
        "```",
        "",
        "No ID should be searched by the user; every option above is already "
        "printed with its exact id.",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(OUT), "unresolved_pairs": unresolved},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
