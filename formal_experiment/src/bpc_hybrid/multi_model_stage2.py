"""Separate Stage 2 model comparison; offline until exact run authorization.

No third-party SDK, automatic retries, Gold reads, or modification of old arms.
The only dotenv read is inside execute(), AFTER validating explicit opt-ins,
the plan bindings, authorization, token limits and verified pricing/budget.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from bpc_hybrid.d1_schema_adapter import adapt_relay_record
from bpc_hybrid.d1_span_canonicalizer import POLICY_LEGACY, canonicalize_record_coordinates
from bpc_hybrid.h1_transport import decode_chat_completion_envelope
from bpc_hybrid.prompt_loader import load_prompt, render_user_prompt
from bpc_hybrid.stage2_canonical import validate_canonical

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "configs/models/stage2_multi_model_v1.json"
RUNS = ROOT / "outputs/development/stage2_multi_model_v1"
TASK = "S2-MODEL-API-SETUP"
PLAN_SCHEMA = "stage2_multi_model_plan@1.0.0"
AUTH_SCHEMA = "stage2_multi_model_authorization@1.0.0"
PARAMETERS = {"temperature", "top_p", "thinking", "enable_thinking", "reasoning_effort"}


class ModelRunError(ValueError):
    """A public, credential-free failure message."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def write_json(path: Path, value: Any, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ModelRunError("无法读取有效 JSON 文件；请检查路径和格式。") from None


def positive_int(value: Any, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ModelRunError(f"{name} 必须是正整数。")
    return value


def positive_number(value: Any, name: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or value <= 0:
        raise ModelRunError(f"{name} 必须是有限正数。")
    return float(value)


def load_catalog(path: Path = CATALOG) -> dict:
    catalog = read_json(path)
    if not isinstance(catalog, dict) or not isinstance(catalog.get("profiles"), dict):
        raise ModelRunError("模型目录格式不合法。")
    if (catalog.get("schema_version") != "stage2_multi_model_catalog@1.0.0"
            or catalog.get("task_id") != TASK or catalog.get("claim_scope") != "development_only"):
        raise ModelRunError("模型目录合同不匹配。")
    if catalog.get("retry") != 0:
        raise ModelRunError("此入口固定不重试。")
    if catalog.get("thinking_requirement") != "disabled":
        raise ModelRunError("此入口必须明确要求全部关闭思考。")
    positive_int(catalog.get("max_output_tokens_per_call"), "单次输出上限")
    positive_number(catalog.get("timeout_seconds"), "超时")
    for name, profile in catalog["profiles"].items():
        if not isinstance(profile, dict):
            raise ModelRunError("模型配置必须是对象。")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ModelRunError("模型家族 ID 不合法。")
        if not re.fullmatch(r"LLM4BPC_[A-Z0-9_]+_API_KEY", profile.get("api_key_env", "")):
            raise ModelRunError("密钥必须使用独立的环境变量。")
        endpoint_url(profile)
        if not isinstance(profile.get("model"), str) or not profile["model"].strip():
            raise ModelRunError("模型 ID 缺失。")
        if profile.get("output_limit_parameter") not in {"max_tokens", "max_completion_tokens"}:
            raise ModelRunError("输出预算参数不合法。")
        if (not isinstance(profile.get("request_parameters"), dict)
                or set(profile["request_parameters"]) - PARAMETERS):
            raise ModelRunError("请求参数包含不允许的字段。")
        parameters = profile["request_parameters"]
        if (profile.get("thinking_mode") != "disabled"
                or ("thinking" in parameters and parameters["thinking"] != {"type": "disabled"})
                or ("enable_thinking" in parameters and parameters["enable_thinking"] is not False)
                or ("reasoning_effort" in parameters and parameters["reasoning_effort"] != "none")):
            raise ModelRunError("模型配置必须关闭思考；low 或省略开关不能代替关闭。")
        if name == "qwen":
            disabled = parameters.get("enable_thinking") is False
        elif name == "grok":
            disabled = parameters.get("reasoning_effort") == "none"
        else:
            disabled = parameters.get("thinking") == {"type": "disabled"}
        if not disabled:
            raise ModelRunError("缺少该模型家族的显式关闭思考参数。")
        if (not isinstance(profile.get("accepted_returned_models"), list)
                or not profile["accepted_returned_models"]
                or any(not isinstance(m, str) or not m for m in profile["accepted_returned_models"])):
            raise ModelRunError("必须登记允许的返回模型 ID。")
    return catalog


def endpoint_url(profile: Mapping[str, Any]) -> str:
    url = str(profile.get("base_url", ""))
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or "{" in url or "}" in url):
        raise ModelRunError("接口必须是无凭据、无查询参数的完整 HTTPS 地址。")
    return url.rstrip("/") + "/chat/completions"


def init_env(root: Path = ROOT) -> str:
    """Append BLANK slots without opening or inspecting an existing .env."""
    target = root / ".env"
    marker = root / ".tmp/multi_model_env_initialized_v1"
    if marker.exists() and target.exists():
        return "填空区已初始化；未读取或改写已有 .env。"
    template = (root / "configs/multi_model_api_keys.env.example").read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n\n" + template)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    return "已追加六家模型的空白密钥项；原有 .env 内容未读取、未覆盖。"


def _source_bindings(root: Path, catalog_path: Path, prompt_path: Path,
                     input_path: Path) -> dict[str, str]:
    paths = [catalog_path, prompt_path, input_path,
             root / "src/bpc_hybrid/multi_model_stage2.py",
             root / "scripts/stage2_multi_model.py",
             root / "src/bpc_hybrid/prompt_loader.py",
             root / "src/bpc_hybrid/d1_schema_adapter.py",
             root / "src/bpc_hybrid/d1_span_canonicalizer.py",
             root / "src/bpc_hybrid/stage2_canonical.py",
             root / "src/bpc_hybrid/h1_transport.py",
             root / "configs/schemas/stage2_prediction.schema.json"]
    return {p.resolve().relative_to(root.resolve()).as_posix(): digest(p.read_bytes()) for p in paths}


def build_plan(providers: list[str], limit: int, run_id: str, *,
               root: Path = ROOT, catalog_path: Path | None = None) -> dict:
    """Freeze provider-specific wire bodies. Never opens dotenv or Gold."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", run_id) or ".." in run_id:
        raise ModelRunError("run_id 只允许字母、数字、点、下划线和短横线。")
    if not providers or len(set(providers)) != len(providers):
        raise ModelRunError("请选择不重复的模型家族。")
    catalog_path = catalog_path or root / "configs/models/stage2_multi_model_v1.json"
    catalog = load_catalog(catalog_path)
    if set(providers) - set(catalog["profiles"]):
        raise ModelRunError("存在未登记的模型家族。")
    if type(limit) is not int or not 1 <= limit <= 150:
        raise ModelRunError("每家样本数必须在 1 到 150 之间。")
    input_path = root / catalog["input_path"]
    # Only the executable, Gold-blind input is available to this runner.
    if input_path.resolve() != (root / "data/input/estg150_formal_inference_input_v2.json").resolve():
        raise ModelRunError("只能使用固定的 EStG-150 推理输入。")
    rows = read_json(input_path).get("records", [])
    if len(rows) != 150 or len({r["sample_id"] for r in rows}) != 150:
        raise ModelRunError("冻结输入必须包含 150 个唯一 sample_id。")
    prompt_name = catalog["prompt_name"]
    if prompt_name != "direct_llm_sun_record_prompt_v6_d1r1_2026_08_05":
        raise ModelRunError("本入口仅比较固定 v6；其他提示词须独立任务。")
    prompt = load_prompt(prompt_name)
    start, end = prompt.raw_text.find("## Examples"), prompt.raw_text.find("## Notes")
    if start < 0 or end <= start:
        raise ModelRunError("固定 v6 的示例区缺失。")
    few_shot_block = prompt.raw_text[start:end].strip()
    requests = []
    # Sample-major ordering interleaves providers using the same selected IDs.
    for row in rows[:limit]:
        sid, text = row["sample_id"], row["approved_text_en"]
        if (not re.fullmatch(r"[A-Za-z0-9_-]+", sid) or not isinstance(text, str)
                or not text or row.get("input_text_sha256") != digest(text.encode("utf-8"))):
            raise ModelRunError("冻结输入的 ID、英文文本或文本哈希不合法。")
        user = render_user_prompt(prompt.user_prompt_template, sample_id=sid,
                                  source_id=sid, source_text=text, few_shot_block=few_shot_block)
        for provider in providers:
            profile = catalog["profiles"][provider]
            body = {"model": profile["model"], "messages": [
                {"role": "system", "content": prompt.system_prompt},
                {"role": "user", "content": user}], "stream": False,
                profile["output_limit_parameter"]: catalog["max_output_tokens_per_call"],
                **copy.deepcopy(profile["request_parameters"])}
            raw = encode(body)
            requests.append({"request_id": f"{provider}:{sid}", "provider": provider,
                             "sample_id": sid, "source_id": sid, "source_text": text,
                             "body": body, "body_sha256": digest(raw),
                             "input_token_reservation": len(raw) + 4096})
    return {"schema_version": PLAN_SCHEMA, "task_id": TASK, "run_id": run_id,
            "claim_scope": "development_only", "authorized": False,
            "thinking_requirement": "disabled",
            "providers": providers, "samples_per_provider": limit,
            "planned_calls": len(requests), "retry": 0,
            "max_output_tokens_per_call": catalog["max_output_tokens_per_call"],
            "timeout_seconds": catalog["timeout_seconds"],
            "profiles": {p: catalog["profiles"][p] for p in providers},
            "bindings": _source_bindings(root, catalog_path, prompt.path, input_path),
            "canonicalization_policy": POLICY_LEGACY,
            "input_token_policy": "UTF-8 wire bytes + 4096 per request; conservative planning reservation, not tokenizer/billing count; stop if actual usage exceeds it",
            "metrics": None, "requests": requests}


def authorization_template(plan: dict) -> dict:
    return {"schema_version": AUTH_SCHEMA, "task_id": TASK, "run_id": plan["run_id"],
            "authorized": False, "user_authorization": "", "approved_at_utc": "",
            "plan_sha256": digest(encode(plan)), "providers": plan["providers"],
            "max_calls": plan["planned_calls"], "retry": 0,
            "max_total_output_tokens": plan["planned_calls"] * plan["max_output_tokens_per_call"],
            "budgets": {p: {"currency": "CNY" if p != "grok" else "USD",
                            "max_cost": None, "input_per_million": None,
                            "output_per_million": None, "pricing_source": "",
                            "pricing_verified_at_utc": ""} for p in plan["providers"]}}


def verify_authorization(plan: dict, auth: dict, *, execute: bool, allow_llm: bool,
                         root: Path = ROOT) -> None:
    """All checks run BEFORE credentials can be loaded or the network touched."""
    if not execute or not allow_llm:
        raise ModelRunError("真实调用必须同时提供 --execute 和 --allow-llm，并获得本次用户授权。")
    if (auth.get("schema_version") != AUTH_SCHEMA or auth.get("authorized") is not True
            or auth.get("task_id") != TASK or auth.get("run_id") != plan.get("run_id")
            or auth.get("plan_sha256") != digest(encode(plan))
            or auth.get("providers") != plan.get("providers")
            or not isinstance(auth.get("user_authorization"), str)
            or not auth["user_authorization"].strip() or not auth.get("approved_at_utc")):
        raise ModelRunError("授权缺失或与本次计划不匹配；历史额度不能复用。")
    if (plan.get("schema_version") != PLAN_SCHEMA or plan.get("task_id") != TASK
            or plan.get("retry") != 0 or auth.get("retry") != 0):
        raise ModelRunError("计划/授权合同不合法。")
    positive_int(auth.get("max_calls"), "调用预算")
    positive_int(auth.get("max_total_output_tokens"), "总输出预算")
    if (auth["max_calls"] != plan["planned_calls"]
            or auth["max_total_output_tokens"] != plan["planned_calls"] * plan["max_output_tokens_per_call"]):
        raise ModelRunError("调用或输出预算与冻结计划不一致。")
    # Rebuild from fixed, non-secret source paths instead of reading paths
    # supplied by an untrusted plan (which could otherwise point at .env).
    fresh = build_plan(plan["providers"], plan["samples_per_provider"], plan["run_id"], root=root)
    if encode(fresh) != encode(plan):
        raise ModelRunError("代码、配置、输入、提示词或请求集合已变化；须重新预检并授权。")
    budgets = auth.get("budgets", {})
    for provider in plan["providers"]:
        budget = budgets.get(provider, {})
        if (budget.get("currency") not in {"CNY", "USD"}
                or not str(budget.get("pricing_source", "")).startswith("https://")
                or not budget.get("pricing_verified_at_utc")):
            raise ModelRunError("每家模型都须记录已核对价格、币种与来源。")
        positive_number(budget.get("max_cost"), "费用上限")
        positive_number(budget.get("input_per_million"), "输入单价")
        positive_number(budget.get("output_per_million"), "输出单价")
        ceiling = sum(_reservation(r, plan, budget) for r in plan["requests"] if r["provider"] == provider)
        if ceiling > budget["max_cost"]:
            raise ModelRunError("费用上限不足以覆盖冻结计划的保守预算；不会自动扩大额度。")


def _reservation(request: dict, plan: dict, budget: dict) -> float:
    return (request["input_token_reservation"] * budget["input_per_million"]
            + plan["max_output_tokens_per_call"] * budget["output_per_million"]) / 1_000_000


def load_credentials(profiles: Mapping[str, dict], root: Path = ROOT) -> dict[str, str]:
    """Private runtime loader; only authorized execution may call it.

    No interpolation, shell evaluation, logging or global environment mutation.
    Unselected keys are never returned. Duplicate conflicting filled slots fail.
    """
    needed = {p["api_key_env"] for p in profiles.values()}
    values: dict[str, str] = {}
    path = root / ".env"
    try:
        with path.open(encoding="utf-8-sig") as handle:
            for raw in handle:
                line = raw.strip()
                if line.startswith("export "):
                    line = line[7:].lstrip()
                key, sep, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not sep or key not in needed or not value:
                    continue
                if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
                    value = value[1:-1]
                else:
                    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
                if not value:
                    continue
                if key in values and values[key] != value:
                    raise ModelRunError("选中模型的 .env 密钥存在重复且冲突的填写项。")
                values[key] = value
    except FileNotFoundError:
        pass
    except OSError:
        raise ModelRunError("无法读取 .env；未发送请求。") from None
    result = {}
    for provider, profile in profiles.items():
        key_name = profile["api_key_env"]
        value = os.environ.get(key_name, "").strip() or values.get(key_name, "")
        if (not value or value.lower().startswith(("your_", "replace_", "填", "<"))
                or any(c.isspace() for c in value)):
            raise ModelRunError(f"{key_name} 尚未有效填写；未发送任何请求。")
        result[provider] = value
    return result


def redact(value: Any, secrets: list[str]) -> Any:
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, "[REDACTED]")
        return value
    if isinstance(value, list):
        return [redact(v, secrets) for v in value]
    if isinstance(value, dict):
        return {redact(k, secrets): redact(v, secrets) for k, v in value.items()}
    return value


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelRunError("接口返回重定向；拒绝转发凭据或自动重发。")


def send_http(profile: dict, body: bytes, api_key: str, timeout: float) -> bytes:
    """One POST, verified TLS, no SDK retries, no credential-bearing redirects."""
    request = urllib.request.Request(endpoint_url(profile), data=body, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + api_key,
                                              "User-Agent": "LLM4BPC-MultiModel/1.0"})
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise ModelRunError("响应超过保存上限；该次调用状态待核查，不自动重试。")
            return raw
    except urllib.error.HTTPError as exc:
        # Preserve diagnostics for incompatible provider parameters; redact
        # both the key and any echoed Authorization header before surfacing it.
        try:
            detail = exc.read(4096).decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        detail = redact(detail, [api_key])
        detail = re.sub(r"(?i)Bearer\s+\S+", "Bearer [REDACTED]", detail)
        raise ModelRunError(f"HTTP {exc.code}: {detail}") from None
    except ModelRunError:
        raise
    except Exception as exc:
        raise ModelRunError(f"传输失败（{type(exc).__name__}；详细凭据信息不输出）。") from None


def verify_nonthinking_response(decoded: dict) -> dict:
    """Reject reported reasoning; absent token detail remains unknown, not zero."""
    reasoning_tokens = decoded.get("usage", {}).get("reasoning_tokens")
    if (decoded.get("reasoning_present")
            or (reasoning_tokens is not None and (type(reasoning_tokens) is not int or reasoning_tokens != 0))
            or decoded.get("content", "").lstrip().startswith("<think>")):
        raise ModelRunError("响应出现思考内容或思考用量，与全部关闭思考的要求不符；停止且不重试。")
    return {"status": "no_reported_reasoning", "reasoning_content_present": False,
            "reported_reasoning_tokens": reasoning_tokens}


def canonical_prediction(request: dict, content: str) -> dict:
    result = {"provider": request["provider"], "sample_id": request["sample_id"],
              "request_id": request["request_id"], "request_status": "failed",
              "failure_stage": None, "record": {}, "canonicalization_policy": POLICY_LEGACY}
    try:
        # Thinking prefixes are forbidden in this non-thinking-only runner.
        text = content.strip()
        if text.startswith("```json\n") and text.endswith("```"):
            text = text[8:-3].strip()
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("non-object")
    except (ValueError, TypeError):
        result["failure_stage"] = "json_parse"
        return result
    for field in ("sample_id", "source_id", "source_text"):
        if payload.get(field) != request[field]:
            result["failure_stage"] = "input_binding"
            return result
    try:
        record, adapter = adapt_relay_record(copy.deepcopy(payload), request["source_text"])
        result["adapter_audit"] = adapter
        if adapter.get("status") == "failed":
            result["failure_stage"] = "adapter"
            return result
        record, coordinates = canonicalize_record_coordinates(record, request["source_text"], policy=POLICY_LEGACY)
        result["canonicalizer_audit"] = coordinates
        if coordinates.get("status") == "failed":
            result["failure_stage"] = "canonicalizer"
            return result
        report = validate_canonical(record)
        result["runtime_validation"] = report.to_dict()
        if not report.schema_valid or not report.cross_field_valid:
            result["failure_stage"] = "canonical_validation"
            return result
        result.update(request_status="ok", record=record)
    except Exception as exc:
        result["failure_stage"] = "conversion_exception"
        result["error_type"] = type(exc).__name__
    return result


def _append_ledger(path: Path, event: dict, previous: str) -> str:
    event = {**event, "previous_sha256": previous}
    event["event_sha256"] = digest(encode(event))
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(encode(event).decode("utf-8") + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return event["event_sha256"]


def _load_ledger(path: Path, plan: dict) -> tuple[dict, dict, str]:
    starts, finishes, previous = {}, {}, ""
    if not path.exists():
        return starts, finishes, previous
    requests = {r["request_id"]: r for r in plan["requests"]}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            observed = event.pop("event_sha256")
            if event.get("previous_sha256") != previous or digest(encode(event)) != observed:
                raise ValueError("chain")
            previous = observed
            rid = event["request_id"]
            if rid not in requests or event.get("plan_sha256") != digest(encode(plan)):
                raise ValueError("identity")
            if event["event"] == "started" and rid not in starts:
                if event.get("body_sha256") != requests[rid]["body_sha256"]:
                    raise ValueError("payload")
                starts[rid] = event
            elif event["event"] == "finished" and rid in starts and rid not in finishes:
                finishes[rid] = event
            else:
                raise ValueError("duplicate")
    except (ValueError, KeyError, TypeError):
        raise ModelRunError("调用账本损坏、身份不匹配或重复；拒绝继续发送。") from None
    return starts, finishes, previous


def _verify_saved_calls(out: Path, plan: dict, auth: dict, starts: dict, finishes: dict) -> None:
    """Verify all previous artifacts and costs before ANY subsequent send."""
    auth_hash = digest(encode(auth))
    for request in plan["requests"]:
        rid, provider = request["request_id"], request["provider"]
        relative = f"responses/{provider}_{request['sample_id']}.json"
        response_path = out / relative
        if rid not in starts:
            if response_path.exists():
                raise ModelRunError("未调用请求已有响应文件；拒绝覆盖或发送。")
            continue
        start = starts[rid]
        budget = auth["budgets"][provider]
        reserve = _reservation(request, plan, budget)
        for field, expected in (("provider", provider), ("sample_id", request["sample_id"]),
                                ("authorization_sha256", auth_hash), ("currency", budget["currency"]),
                                ("reserved_cost", reserve)):
            if start.get(field) != expected:
                raise ModelRunError("历史调用的授权、身份或预留费用不匹配。")
        finish = finishes.get(rid)
        if finish is None:
            continue  # The caller rejects all uncertain/incomplete attempts.
        if (finish.get("response_path") != relative
                or finish.get("provider") != provider
                or finish.get("sample_id") != request["sample_id"]
                or finish.get("authorization_sha256") != auth_hash
                or finish.get("currency") != budget["currency"]
                or type(finish.get("needs_attention")) is not bool
                or not response_path.is_file()
                or digest(response_path.read_bytes()) != finish.get("response_sha256")):
            raise ModelRunError("历史响应文件、调用身份或授权与账本不匹配。")
        saved = read_json(response_path)
        if saved.get("request_id") != rid or saved.get("prediction", {}).get("request_id") != rid:
            raise ModelRunError("历史响应的请求 ID 不匹配。")
        if not finish["needs_attention"]:
            usage = saved.get("usage", {})
            pt, ct = usage.get("prompt_tokens"), usage.get("completion_tokens")
            if (type(pt) is not int or type(ct) is not int or pt < 0 or ct < 0
                    or pt > request["input_token_reservation"] or ct > plan["max_output_tokens_per_call"]):
                raise ModelRunError("历史 token 用量不合法。")
            reserve = (pt * budget["input_per_million"] + ct * budget["output_per_million"]) / 1_000_000
        if (type(finish.get("reserved_cost")) not in (float, int)
                or finish["reserved_cost"] != reserve):
            raise ModelRunError("历史费用与保存用量不匹配。")


def execute_plan(plan: dict, auth: dict, *, execute: bool = False,
                 allow_llm: bool = False, resume: bool = False, root: Path = ROOT,
                 sender: Callable = send_http, credential_loader: Callable = load_credentials) -> dict:
    verify_authorization(plan, auth, execute=execute, allow_llm=allow_llm, root=root)
    out = root / "outputs/development/stage2_multi_model_v1" / plan["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    lock = out / ".run.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ModelRunError("运行锁已存在；可能有另一进程或中断待核查，拒绝重复调用。") from None
    os.close(fd)
    try:
        ledger = out / "calls_ledger.jsonl"
        if ledger.exists() and not resume:
            raise ModelRunError("运行已存在；只能显式 --resume，不能覆盖或重新发送。")
        if (out / "manifest.json").exists() and not ledger.exists():
            raise ModelRunError("产物存在但账本缺失；拒绝覆盖或重新发送。")
        starts, finishes, previous = _load_ledger(ledger, plan)
        auth_hash = digest(encode(auth))
        snapshot = out / "authorization_snapshot.json"
        if snapshot.exists() and digest(encode(read_json(snapshot))) != auth_hash:
            raise ModelRunError("恢复运行的授权记录已变化；拒绝继续发送。")
        if starts and not snapshot.exists():
            raise ModelRunError("已有调用的授权快照缺失；拒绝继续发送。")
        _verify_saved_calls(out, plan, auth, starts, finishes)
        if set(starts) - set(finishes) or any(f["needs_attention"] for f in finishes.values()):
            raise ModelRunError("存在已尝试但结果/计费不确定的请求；须人工核查，不能自动重发。")
        # Validate every selected key before the first send. No keys are placed
        # in plan, auth snapshots, repr, stdout, logs or manifests.
        credentials = credential_loader(plan["profiles"], root) if len(starts) < plan["planned_calls"] else {}
        secrets = list(credentials.values())
        if not snapshot.exists():
            write_json(snapshot, redact(auth, secrets), exclusive=True)
        spent = {p: sum(f["reserved_cost"] for f in finishes.values() if f["provider"] == p)
                 for p in plan["providers"]}
        for request in plan["requests"]:
            rid, provider = request["request_id"], request["provider"]
            if rid in starts:
                continue
            body = encode(request["body"])
            if digest(body) != request["body_sha256"]:
                raise ModelRunError("发送前请求哈希变化；拒绝发送。")
            if len(starts) >= auth["max_calls"]:
                raise ModelRunError("调用额度已用尽。")
            budget = auth["budgets"][provider]
            reserve = _reservation(request, plan, budget)
            if spent[provider] + reserve > budget["max_cost"]:
                raise ModelRunError("发送前费用预留超过授权上限。")
            base = {"request_id": rid, "provider": provider, "sample_id": request["sample_id"],
                    "plan_sha256": digest(encode(plan)), "body_sha256": request["body_sha256"],
                    "authorization_sha256": auth_hash, "timestamp_utc": now(),
                    "reserved_cost": reserve, "currency": budget["currency"]}
            previous = _append_ledger(ledger, {**base, "event": "started"}, previous)
            starts[rid] = base
            raw_text, error, usage, returned_model, prediction = "", None, {}, None, {}
            nonthinking_check = {"status": "not_verified", "reported_reasoning_tokens": None}
            needs_attention = False
            try:
                raw = sender(plan["profiles"][provider], body, credentials[provider], plan["timeout_seconds"])
                decoded = decode_chat_completion_envelope(raw)
                raw_text = raw.decode("utf-8", errors="replace")
                usage, returned_model = decoded.get("usage", {}), decoded.get("model")
                if returned_model not in plan["profiles"][provider]["accepted_returned_models"]:
                    raise ModelRunError("返回模型与授权型号不匹配或缺失；停止运行。")
                prompt_tokens = usage.get("prompt_tokens")
                completion_tokens = usage.get("completion_tokens")
                if (type(prompt_tokens) is not int or type(completion_tokens) is not int
                        or prompt_tokens < 0 or completion_tokens < 0
                        or prompt_tokens > request["input_token_reservation"]
                        or completion_tokens > plan["max_output_tokens_per_call"]):
                    raise ModelRunError("usage 缺失/不合法或超过预算；保留该次费用预留并停止。")
                if decoded.get("status") != "ok_message_content" or decoded.get("finish_reason") != "stop":
                    raise ModelRunError("响应为空、不完整或非文本完成；停止且不重试。")
                nonthinking_check = verify_nonthinking_response(decoded)
                prediction = canonical_prediction(request, decoded["content"])
                reserve = (prompt_tokens * budget["input_per_million"]
                           + completion_tokens * budget["output_per_million"]) / 1_000_000
            except Exception as exc:
                needs_attention = True
                error = str(exc) if isinstance(exc, ModelRunError) else f"运行异常（{type(exc).__name__}）。"
                prediction = {"provider": provider, "sample_id": request["sample_id"],
                              "request_id": rid, "request_status": "failed",
                              "failure_stage": "transport_or_usage", "record": {}}
            response_path = out / "responses" / f"{provider}_{request['sample_id']}.json"
            result = redact({"request_id": rid, "raw_response_utf8": raw_text,
                             "usage": usage, "returned_model": returned_model,
                             "nonthinking_check": nonthinking_check,
                             "error": error, "prediction": prediction}, secrets)
            write_json(response_path, result, exclusive=True)
            finish = {**base, "event": "finished", "reserved_cost": reserve,
                      "needs_attention": needs_attention,
                      "response_path": response_path.relative_to(out).as_posix(),
                      "response_sha256": digest(response_path.read_bytes()),
                      "request_status": prediction["request_status"]}
            previous = _append_ledger(ledger, finish, previous)
            finishes[rid] = finish
            spent[provider] += reserve
            if needs_attention:
                break
        predictions = []
        for request in plan["requests"]:
            finish = finishes.get(request["request_id"])
            if finish:
                response_path = out / finish["response_path"]
                if digest(response_path.read_bytes()) != finish["response_sha256"]:
                    raise ModelRunError("保存响应的字节与账本不匹配。")
                predictions.append(read_json(response_path)["prediction"])
            else:
                predictions.append({"provider": request["provider"], "sample_id": request["sample_id"],
                                    "request_id": request["request_id"], "request_status": "not_attempted",
                                    "failure_stage": "not_attempted", "record": {}})
        write_json(out / "predictions.json", {"claim_scope": "development_only", "records": predictions})
        complete = len(finishes) == len(plan["requests"]) and not any(f["needs_attention"] for f in finishes.values())
        manifest = {"schema_version": "stage2_multi_model_manifest@1.0.0", "task_id": TASK,
                    "run_id": plan["run_id"], "timestamp_utc": now(), "status": "succeeded" if complete else "partial",
                    "claim_scope": "development_only", "real_api": True, "llm_calls": len(starts),
                    "planned_calls": plan["planned_calls"], "retry": 0, "metrics": None,
                    "thinking_requirement": "disabled",
                    "gold_read_by_runner": False, "plan_sha256": digest(encode(plan)),
                    "authorization_sha256": auth_hash, "profiles": plan["profiles"], "bindings": plan["bindings"],
                    "canonicalization_policy": POLICY_LEGACY, "ledger_head_sha256": previous,
                    "conservative_uncached_cost_by_provider": spent,
                    "predictions_sha256": digest((out / "predictions.json").read_bytes()),
                    "valid_predictions": sum(r["request_status"] == "ok" for r in predictions),
                    "failed_or_unattempted_predictions": sum(r["request_status"] != "ok" for r in predictions)}
        write_json(out / "manifest.json", manifest)
        return manifest
    finally:
        lock.unlink(missing_ok=True)
