"""Deterministic S1.1/S1.2/S1.4 BPMN structural Process Records.

This module is offline and method-independent.  It parses one BPMN process,
preserves original labels, derives control-flow relations, and validates the
result against the frozen Process Record schema.  It does not infer label
semantics, read human Gold, or evaluate performance.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "process_record@1.0.0"
CONTRACT_VERSION = "stage1_structural_contract@1.0.0"
PARSER_VERSION = "stage1_bpmn_parser@1.0.0"
METHOD_NAME = "stage1_bpmn_xml_structural"
CANONICAL_NAMESPACE = "http://www.omg.org/spec/BPMN/20100524/MODEL"
ACTIVITY_TYPES = (
    "task",
    "userTask",
    "serviceTask",
    "sendTask",
    "receiveTask",
    "manualTask",
    "businessRuleTask",
    "scriptTask",
    "subProcess",
    "callActivity",
)
EVENT_TYPES = (
    "startEvent",
    "endEvent",
    "intermediateCatchEvent",
    "intermediateThrowEvent",
    "boundaryEvent",
)
GATEWAY_TYPES = (
    "exclusiveGateway",
    "parallelGateway",
    "inclusiveGateway",
    "complexGateway",
    "eventBasedGateway",
)


class Stage1ProcessError(ValueError):
    """Raised when the Stage 1 structural contract fails closed."""


@dataclass(frozen=True)
class ProcessValidationReport:
    schema_valid: bool
    cross_field_valid: bool
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return self.schema_valid and self.cross_field_valid

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_valid": self.schema_valid,
            "cross_field_valid": self.cross_field_valid,
            "errors": list(self.errors),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_stage1_contract(path: Path) -> dict[str, Any]:
    try:
        contract = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Stage1ProcessError(f"invalid Stage 1 structural contract: {path}") from exc
    if not isinstance(contract, dict):
        raise Stage1ProcessError("Stage 1 structural contract root must be an object")
    if (
        contract.get("schema_version") != CONTRACT_VERSION
        or contract.get("task_ids") != ["S1.1", "S1.2", "S1.4"]
    ):
        raise Stage1ProcessError("Stage 1 structural contract identity changed")
    parser = contract.get("parser", {})
    if (
        parser.get("method_name") != METHOD_NAME
        or parser.get("parser_version") != PARSER_VERSION
        or parser.get("input_extension") != ".bpmn"
        or parser.get("canonical_namespace") != CANONICAL_NAMESPACE
        or parser.get("process_selection") != "exactly_one_process_per_input"
        or parser.get("subprocess_handling") != "opaque_activity_no_internal_flattening"
        or parser.get("label_semantics") != "preserve_original_labels_only"
        or parser.get("xml_doctype_or_entity_allowed") is not False
        or parser.get("max_input_bytes") != 20_971_520
    ):
        raise Stage1ProcessError("Stage 1 parser contract changed")
    supported = contract.get("supported_elements", {})
    if (
        tuple(supported.get("activities", ())) != ACTIVITY_TYPES
        or tuple(supported.get("events", ())) != EVENT_TYPES
        or tuple(supported.get("gateways", ())) != GATEWAY_TYPES
        or supported.get("containers") != ["participant", "lane", "sequenceFlow"]
    ):
        raise Stage1ProcessError("Stage 1 supported BPMN element set changed")
    determinism = contract.get("determinism", {})
    if (
        determinism.get("record_arrays") != "ascending_id"
        or determinism.get("id_lists") != "ascending_codepoint"
        or determinism.get("edge_pairs") != "ascending_source_ref_then_target_ref"
        or determinism.get("xml_sibling_order_affects_output") is not False
        or determinism.get("duplicate_ids") != "reject"
        or determinism.get("unknown_flow_references") != "reject"
        or determinism.get("orphan_lane_references") != "reject"
    ):
        raise Stage1ProcessError("Stage 1 determinism contract changed")
    control = contract.get("control_flow", {})
    if control != {
        "direct_edges": "one_pair_per_sequence_flow_deduplicated",
        "reachable_pairs": "directed_transitive_reachability_excluding_self_pairs",
        "activity_order_relations": "reachable_activity_pairs_excluding_self_pairs",
        "cycle_detection": "nodes_that_can_reach_themselves_via_one_or_more_edges",
        "unreachable_nodes": "flow_nodes_not_reachable_from_any_start_event_including_start_events_as_reachable",
        "branching_gateway": "gateway_outdegree_greater_than_one",
        "parallel_split": "parallelGateway_outdegree_greater_than_one",
        "parallel_join": "parallelGateway_indegree_greater_than_one",
    }:
        raise Stage1ProcessError("Stage 1 control-flow semantics changed")
    schema_spec = contract.get("process_record_schema", {})
    schema_path = _project_path(str(schema_spec.get("path", "")))
    if (
        schema_spec.get("schema_version") != SCHEMA_VERSION
        or not schema_path.is_file()
        or sha256_file(schema_path) != schema_spec.get("sha256")
    ):
        raise Stage1ProcessError("Stage 1 Process Record schema binding changed")
    safety = contract.get("safety", {})
    if (
        safety.get("fixture_scope") != "synthetic_only"
        or safety.get("formal_bpmn_read") is not False
        or safety.get("human_gold_read_or_modified") is not False
        or safety.get("llm_api_called") is not False
        or safety.get("network_called") is not False
        or safety.get("performance_evaluation") is not False
        or safety.get("formal_process_records_written") is not False
        or safety.get("no_overwrite") is not True
    ):
        raise Stage1ProcessError("Stage 1 safety boundary changed")
    return contract


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _namespace(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") and "}" in tag else ""


def _required_id(element: ET.Element, label: str) -> str:
    value = (element.get("id") or "").strip()
    if not value:
        raise Stage1ProcessError(f"{label} requires a non-empty id")
    return value


def _name(element: ET.Element) -> str:
    return element.get("name") or ""


def _pair_dicts(pairs: set[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"source_ref": source, "target_ref": target}
        for source, target in sorted(pairs)
    ]


def _graph_relations(
    node_ids: Sequence[str],
    direct_pairs: set[tuple[str, str]],
    start_ids: Sequence[str],
) -> tuple[set[tuple[str, str]], set[str], set[str], dict[str, set[str]], dict[str, set[str]]]:
    successors = {node_id: set() for node_id in node_ids}
    predecessors = {node_id: set() for node_id in node_ids}
    for source, target in direct_pairs:
        successors[source].add(target)
        predecessors[target].add(source)

    reachable: set[tuple[str, str]] = set()
    cyclic: set[str] = set()
    for source in node_ids:
        seen: set[str] = set()
        stack = list(successors[source])
        while stack:
            target = stack.pop()
            if target in seen:
                continue
            seen.add(target)
            stack.extend(successors[target] - seen)
        if source in seen:
            cyclic.add(source)
        reachable.update((source, target) for target in seen if target != source)

    from_start: set[str] = set(start_ids)
    stack = list(start_ids)
    while stack:
        source = stack.pop()
        for target in successors[source]:
            if target not in from_start:
                from_start.add(target)
                stack.append(target)
    unreachable = set(node_ids) - from_start
    return reachable, cyclic, unreachable, successors, predecessors


def _collect_lanes(process: ET.Element) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []

    def walk(container: ET.Element, parent_lane_id: str | None) -> None:
        for child in list(container):
            if _local_name(child.tag) not in {"laneSet", "childLaneSet"}:
                continue
            for lane in list(child):
                if _local_name(lane.tag) != "lane":
                    continue
                lane_id = _required_id(lane, "lane")
                refs = sorted(
                    {
                        (ref.text or "").strip()
                        for ref in list(lane)
                        if _local_name(ref.tag) == "flowNodeRef" and (ref.text or "").strip()
                    }
                )
                lanes.append(
                    {
                        "id": lane_id,
                        "name": _name(lane),
                        "parent_lane_id": parent_lane_id,
                        "flow_node_refs": refs,
                    }
                )
                walk(lane, lane_id)

    walk(process, None)
    return sorted(lanes, key=lambda item: item["id"])


def _schema_errors(record: Mapping[str, Any], schema_path: Path) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return _manual_schema_errors(record)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(record), key=lambda item: tuple(str(part) for part in item.path)
    ):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"jsonschema:{location}:{error.message}")
    return errors


def _manual_schema_errors(record: Mapping[str, Any]) -> list[str]:
    """Exact in-process schema fallback for the frozen Process Record v1."""

    errors: list[str] = []

    def exact_keys(value: Any, required: set[str], label: str) -> bool:
        if not isinstance(value, Mapping):
            errors.append(f"{label} must be an object")
            return False
        if set(value) != required:
            errors.append(f"{label} keys are not exact")
            return False
        return True

    def nonempty(value: Any, label: str) -> bool:
        if not isinstance(value, str) or not value:
            errors.append(f"{label} must be a non-empty string")
            return False
        return True

    def id_array(value: Any, label: str) -> bool:
        if (
            not isinstance(value, list)
            or any(not isinstance(item, str) or not item for item in value)
            or len(value) != len(set(value))
        ):
            errors.append(f"{label} must be a unique non-empty string array")
            return False
        return True

    top_keys = {
        "schema_version",
        "process_id",
        "source",
        "method",
        "pools",
        "lanes",
        "activities",
        "events",
        "gateways",
        "sequence_flows",
        "control_flow",
    }
    if not exact_keys(record, top_keys, "record"):
        return errors
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("record.schema_version changed")
    nonempty(record.get("process_id"), "record.process_id")

    source = record.get("source")
    if exact_keys(source, {"input_id", "path", "sha256", "byte_size", "bpmn_namespace"}, "source"):
        nonempty(source.get("input_id"), "source.input_id")
        nonempty(source.get("path"), "source.path")
        digest = source.get("sha256")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            errors.append("source.sha256 must be lowercase SHA-256")
        if isinstance(source.get("byte_size"), bool) or not isinstance(source.get("byte_size"), int) or source["byte_size"] < 1:
            errors.append("source.byte_size must be a positive integer")
        if not isinstance(source.get("bpmn_namespace"), str):
            errors.append("source.bpmn_namespace must be a string")

    method = record.get("method")
    if exact_keys(method, {"name", "parser_version", "label_semantics"}, "method"):
        if method.get("name") != METHOD_NAME:
            errors.append("method.name changed")
        if method.get("parser_version") != PARSER_VERSION:
            errors.append("method.parser_version changed")
        if method.get("label_semantics") != "preserve_original_labels_only":
            errors.append("method.label_semantics changed")

    for collection in ("pools", "lanes", "activities", "events", "gateways", "sequence_flows"):
        if not isinstance(record.get(collection), list):
            errors.append(f"{collection} must be an array")

    if errors:
        return errors
    for index, pool in enumerate(record["pools"]):
        label = f"pools[{index}]"
        if exact_keys(pool, {"id", "name", "process_ref"}, label):
            nonempty(pool.get("id"), f"{label}.id")
            if not isinstance(pool.get("name"), str):
                errors.append(f"{label}.name must be a string")
            nonempty(pool.get("process_ref"), f"{label}.process_ref")
    for index, lane in enumerate(record["lanes"]):
        label = f"lanes[{index}]"
        if exact_keys(lane, {"id", "name", "parent_lane_id", "flow_node_refs"}, label):
            nonempty(lane.get("id"), f"{label}.id")
            if not isinstance(lane.get("name"), str):
                errors.append(f"{label}.name must be a string")
            parent = lane.get("parent_lane_id")
            if parent is not None:
                nonempty(parent, f"{label}.parent_lane_id")
            id_array(lane.get("flow_node_refs"), f"{label}.flow_node_refs")
    for collection in ("activities", "events", "gateways"):
        for index, node in enumerate(record[collection]):
            label = f"{collection}[{index}]"
            if exact_keys(node, {"id", "name", "type", "lane_ids"}, label):
                nonempty(node.get("id"), f"{label}.id")
                if not isinstance(node.get("name"), str):
                    errors.append(f"{label}.name must be a string")
                nonempty(node.get("type"), f"{label}.type")
                id_array(node.get("lane_ids"), f"{label}.lane_ids")
    for index, flow in enumerate(record["sequence_flows"]):
        label = f"sequence_flows[{index}]"
        keys = {"id", "name", "source_ref", "target_ref", "condition_expression", "is_default"}
        if exact_keys(flow, keys, label):
            nonempty(flow.get("id"), f"{label}.id")
            if not isinstance(flow.get("name"), str):
                errors.append(f"{label}.name must be a string")
            nonempty(flow.get("source_ref"), f"{label}.source_ref")
            nonempty(flow.get("target_ref"), f"{label}.target_ref")
            if flow.get("condition_expression") is not None and not isinstance(flow.get("condition_expression"), str):
                errors.append(f"{label}.condition_expression must be string/null")
            if not isinstance(flow.get("is_default"), bool):
                errors.append(f"{label}.is_default must be boolean")

    control = record.get("control_flow")
    control_keys = {
        "direct_edges",
        "reachable_pairs",
        "activity_order_relations",
        "start_event_ids",
        "end_event_ids",
        "branching_gateway_ids",
        "parallel_gateway_ids",
        "parallel_split_gateway_ids",
        "parallel_join_gateway_ids",
        "cyclic_node_ids",
        "cycle_detected",
        "unreachable_node_ids",
    }
    if exact_keys(control, control_keys, "control_flow"):
        for collection in ("direct_edges", "reachable_pairs"):
            if not isinstance(control.get(collection), list):
                errors.append(f"control_flow.{collection} must be an array")
                continue
            for index, pair in enumerate(control[collection]):
                label = f"control_flow.{collection}[{index}]"
                if exact_keys(pair, {"source_ref", "target_ref"}, label):
                    nonempty(pair.get("source_ref"), f"{label}.source_ref")
                    nonempty(pair.get("target_ref"), f"{label}.target_ref")
        order = control.get("activity_order_relations")
        if not isinstance(order, list):
            errors.append("control_flow.activity_order_relations must be an array")
        else:
            for index, pair in enumerate(order):
                label = f"control_flow.activity_order_relations[{index}]"
                keys = {"before_activity_id", "after_activity_id", "relation"}
                if exact_keys(pair, keys, label):
                    nonempty(pair.get("before_activity_id"), f"{label}.before_activity_id")
                    nonempty(pair.get("after_activity_id"), f"{label}.after_activity_id")
                    if pair.get("relation") != "reachable_before":
                        errors.append(f"{label}.relation changed")
        for key in control_keys - {"direct_edges", "reachable_pairs", "activity_order_relations", "cycle_detected"}:
            id_array(control.get(key), f"control_flow.{key}")
        if not isinstance(control.get("cycle_detected"), bool):
            errors.append("control_flow.cycle_detected must be boolean")
    return errors


def validate_process_record(
    record: Mapping[str, Any],
    *,
    schema_path: Path | None = None,
) -> ProcessValidationReport:
    """Validate schema plus all deterministic cross-field invariants."""

    if not isinstance(record, Mapping):
        return ProcessValidationReport(False, False, ("record must be an object",))
    schema = schema_path or ROOT / "configs" / "schemas" / "process_record.schema.json"
    schema_errors = _schema_errors(record, schema)
    if schema_errors:
        return ProcessValidationReport(False, False, tuple(schema_errors))

    errors: list[str] = []
    pools = record["pools"]
    lanes = record["lanes"]
    activities = record["activities"]
    events = record["events"]
    gateways = record["gateways"]
    flows = record["sequence_flows"]
    control = record["control_flow"]
    collections = {
        "pool": pools,
        "lane": lanes,
        "activity": activities,
        "event": events,
        "gateway": gateways,
        "sequence_flow": flows,
    }
    for label, items in collections.items():
        ids = [item["id"] for item in items]
        if ids != sorted(ids):
            errors.append(f"{label} records are not sorted by id")
        if len(ids) != len(set(ids)):
            errors.append(f"duplicate {label} id")

    all_entity_ids = [
        record["process_id"],
        *[item["id"] for items in collections.values() for item in items],
    ]
    if len(all_entity_ids) != len(set(all_entity_ids)):
        errors.append("supported BPMN entity ids are not globally unique")

    node_groups = (activities, events, gateways)
    node_ids = [item["id"] for group in node_groups for item in group]
    if len(node_ids) != len(set(node_ids)):
        errors.append("flow-node ids are not globally unique")
    node_set = set(node_ids)
    lane_ids = {item["id"] for item in lanes}
    lane_membership: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for lane in lanes:
        if lane["flow_node_refs"] != sorted(lane["flow_node_refs"]):
            errors.append(f"lane {lane['id']} flow_node_refs are not sorted")
        if lane["parent_lane_id"] is not None and lane["parent_lane_id"] not in lane_ids:
            errors.append(f"lane {lane['id']} has an unknown parent")
        for node_id in lane["flow_node_refs"]:
            if node_id not in node_set:
                errors.append(f"lane {lane['id']} references unknown node {node_id}")
            else:
                lane_membership[node_id].add(lane["id"])
    for node in (item for group in node_groups for item in group):
        if node["lane_ids"] != sorted(node["lane_ids"]):
            errors.append(f"node {node['id']} lane_ids are not sorted")
        if set(node["lane_ids"]) != lane_membership[node["id"]]:
            errors.append(f"node/lane membership mismatch for {node['id']}")

    process_id = record["process_id"]
    if any(pool["process_ref"] != process_id for pool in pools):
        errors.append("pool process_ref does not match process_id")

    direct_pairs: set[tuple[str, str]] = set()
    for flow in flows:
        source = flow["source_ref"]
        target = flow["target_ref"]
        if source not in node_set or target not in node_set:
            errors.append(f"sequence flow {flow['id']} has an unknown endpoint")
        else:
            direct_pairs.add((source, target))
    if errors:
        return ProcessValidationReport(True, False, tuple(errors))

    start_ids = sorted(item["id"] for item in events if item["type"] == "startEvent")
    end_ids = sorted(item["id"] for item in events if item["type"] == "endEvent")
    reachable, cyclic, unreachable, successors, predecessors = _graph_relations(
        sorted(node_set), direct_pairs, start_ids
    )
    gateway_by_id = {item["id"]: item for item in gateways}
    branching = sorted(
        node_id for node_id in gateway_by_id if len(successors[node_id]) > 1
    )
    parallel = sorted(
        node_id for node_id, item in gateway_by_id.items() if item["type"] == "parallelGateway"
    )
    parallel_split = sorted(node_id for node_id in parallel if len(successors[node_id]) > 1)
    parallel_join = sorted(node_id for node_id in parallel if len(predecessors[node_id]) > 1)
    activity_ids = {item["id"] for item in activities}
    order = [
        {
            "before_activity_id": source,
            "after_activity_id": target,
            "relation": "reachable_before",
        }
        for source, target in sorted(reachable)
        if source in activity_ids and target in activity_ids
    ]
    expected = {
        "direct_edges": _pair_dicts(direct_pairs),
        "reachable_pairs": _pair_dicts(reachable),
        "activity_order_relations": order,
        "start_event_ids": start_ids,
        "end_event_ids": end_ids,
        "branching_gateway_ids": branching,
        "parallel_gateway_ids": parallel,
        "parallel_split_gateway_ids": parallel_split,
        "parallel_join_gateway_ids": parallel_join,
        "cyclic_node_ids": sorted(cyclic),
        "cycle_detected": bool(cyclic),
        "unreachable_node_ids": sorted(unreachable),
    }
    for key, value in expected.items():
        if control.get(key) != value:
            errors.append(f"control_flow.{key} disagrees with sequence flows")
    return ProcessValidationReport(True, not errors, tuple(errors))


def parse_bpmn_bytes(
    payload: bytes,
    *,
    source_path: str,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Parse one BPMN byte payload into a canonical Process Record."""

    if not isinstance(payload, bytes) or not payload:
        raise Stage1ProcessError("BPMN payload must be non-empty bytes")
    parser_contract = contract["parser"]
    if len(payload) > parser_contract["max_input_bytes"]:
        raise Stage1ProcessError("BPMN payload exceeds the frozen size ceiling")
    if not isinstance(source_path, str) or not source_path or Path(source_path).suffix.lower() != ".bpmn":
        raise Stage1ProcessError("BPMN source_path must be a non-empty .bpmn path")
    upper = payload.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise Stage1ProcessError("BPMN DOCTYPE/entity declarations are forbidden")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise Stage1ProcessError("BPMN XML is not well formed") from exc
    processes = [element for element in root.iter() if _local_name(element.tag) == "process"]
    if len(processes) != 1:
        raise Stage1ProcessError("BPMN input must contain exactly one process")
    process = processes[0]
    process_id = _required_id(process, "process")
    direct_children = list(process)

    lanes = _collect_lanes(process)
    lane_ids_by_node: dict[str, set[str]] = {}
    for lane in lanes:
        for node_id in lane["flow_node_refs"]:
            lane_ids_by_node.setdefault(node_id, set()).add(lane["id"])

    def nodes_of(types: Sequence[str]) -> list[dict[str, Any]]:
        allowed = set(types)
        result = []
        for element in direct_children:
            node_type = _local_name(element.tag)
            if node_type not in allowed:
                continue
            node_id = _required_id(element, node_type)
            result.append(
                {
                    "id": node_id,
                    "name": _name(element),
                    "type": node_type,
                    "lane_ids": sorted(lane_ids_by_node.get(node_id, set())),
                }
            )
        return sorted(result, key=lambda item: item["id"])

    activities = nodes_of(ACTIVITY_TYPES)
    events = nodes_of(EVENT_TYPES)
    gateways = nodes_of(GATEWAY_TYPES)
    all_nodes = activities + events + gateways
    node_ids = [item["id"] for item in all_nodes]
    if len(node_ids) != len(set(node_ids)):
        raise Stage1ProcessError("BPMN flow-node ids must be globally unique")
    node_set = set(node_ids)

    source_defaults = {
        element.get("id"): element.get("default")
        for element in direct_children
        if element.get("id")
    }
    flows: list[dict[str, Any]] = []
    for element in direct_children:
        if _local_name(element.tag) != "sequenceFlow":
            continue
        flow_id = _required_id(element, "sequenceFlow")
        source_ref = (element.get("sourceRef") or "").strip()
        target_ref = (element.get("targetRef") or "").strip()
        if source_ref not in node_set or target_ref not in node_set:
            raise Stage1ProcessError(f"sequence flow {flow_id} references an unknown node")
        conditions = [
            " ".join("".join(child.itertext()).split())
            for child in list(element)
            if _local_name(child.tag) == "conditionExpression"
        ]
        condition = conditions[0] if conditions and conditions[0] else None
        flows.append(
            {
                "id": flow_id,
                "name": _name(element),
                "source_ref": source_ref,
                "target_ref": target_ref,
                "condition_expression": condition,
                "is_default": source_defaults.get(source_ref) == flow_id,
            }
        )
    flows.sort(key=lambda item: item["id"])
    if len({item["id"] for item in flows}) != len(flows):
        raise Stage1ProcessError("duplicate sequence flow id")

    pools = sorted(
        [
            {
                "id": _required_id(element, "participant"),
                "name": _name(element),
                "process_ref": (element.get("processRef") or "").strip(),
            }
            for element in root.iter()
            if _local_name(element.tag) == "participant"
            and (element.get("processRef") or "").strip() == process_id
        ],
        key=lambda item: item["id"],
    )

    direct_pairs = {(item["source_ref"], item["target_ref"]) for item in flows}
    start_ids = sorted(item["id"] for item in events if item["type"] == "startEvent")
    end_ids = sorted(item["id"] for item in events if item["type"] == "endEvent")
    reachable, cyclic, unreachable, successors, predecessors = _graph_relations(
        sorted(node_set), direct_pairs, start_ids
    )
    gateway_by_id = {item["id"]: item for item in gateways}
    branching = sorted(node_id for node_id in gateway_by_id if len(successors[node_id]) > 1)
    parallel = sorted(
        node_id for node_id, item in gateway_by_id.items() if item["type"] == "parallelGateway"
    )
    activity_ids = {item["id"] for item in activities}
    order_relations = [
        {
            "before_activity_id": source,
            "after_activity_id": target,
            "relation": "reachable_before",
        }
        for source, target in sorted(reachable)
        if source in activity_ids and target in activity_ids
    ]
    source_path_normalized = source_path.replace("\\", "/")
    record = {
        "schema_version": SCHEMA_VERSION,
        "process_id": process_id,
        "source": {
            "input_id": Path(source_path_normalized).stem,
            "path": source_path_normalized,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "byte_size": len(payload),
            "bpmn_namespace": _namespace(root.tag),
        },
        "method": {
            "name": METHOD_NAME,
            "parser_version": PARSER_VERSION,
            "label_semantics": "preserve_original_labels_only",
        },
        "pools": pools,
        "lanes": lanes,
        "activities": activities,
        "events": events,
        "gateways": gateways,
        "sequence_flows": flows,
        "control_flow": {
            "direct_edges": _pair_dicts(direct_pairs),
            "reachable_pairs": _pair_dicts(reachable),
            "activity_order_relations": order_relations,
            "start_event_ids": start_ids,
            "end_event_ids": end_ids,
            "branching_gateway_ids": branching,
            "parallel_gateway_ids": parallel,
            "parallel_split_gateway_ids": sorted(
                node_id for node_id in parallel if len(successors[node_id]) > 1
            ),
            "parallel_join_gateway_ids": sorted(
                node_id for node_id in parallel if len(predecessors[node_id]) > 1
            ),
            "cyclic_node_ids": sorted(cyclic),
            "cycle_detected": bool(cyclic),
            "unreachable_node_ids": sorted(unreachable),
        },
    }
    schema_path = _project_path(contract["process_record_schema"]["path"])
    report = validate_process_record(record, schema_path=schema_path)
    if not report.valid:
        raise Stage1ProcessError("invalid Process Record: " + "; ".join(report.errors))
    return copy.deepcopy(record)


def parse_bpmn_file(path: Path, *, contract: Mapping[str, Any]) -> dict[str, Any]:
    file_path = Path(path)
    try:
        payload = file_path.read_bytes()
    except OSError as exc:
        raise Stage1ProcessError(f"cannot read BPMN input: {file_path}") from exc
    try:
        source_path = file_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        source_path = file_path.name
    return parse_bpmn_bytes(payload, source_path=source_path, contract=contract)
