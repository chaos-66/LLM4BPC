# -*- coding: utf-8 -*-
"""Offline readiness report for the two real-LLM comparison batches.

The two batches were authorized on 2026-09-07 (S2.12 batch A = 63 calls;
GDPR batch B = 74 calls).  This script proves, offline and deterministically,
that everything except the process-environment credentials is in place, and
records the exact blocker so the real run can be started the moment the key is
injected by the host.

It performs REAL, fail-closed checks (no simulation of success):

1. every authorization event / contract / preflight asset exists and is
   hash-stable;
2. the offline credential precheck (``check_api_env_ready_v1.py``) is run and
   its verdict is recorded verbatim;
3. the GDPR LLM-SE executor's payload-locked FAKE transport runs the full
   74-call rehearsal in a scratch directory (74/74 complete, 0 calls billed);
4. the executor refuses a real run without its contract file;
5. the promoter refuses the fake capsule (so a rehearsal can never be promoted
   to the formal arm home);
6. the S2.12 runner refuses a real run without credentials.

Zero LLM/API/network.  Nothing under ``data/`` is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

OUT_JSON = ROOT / "outputs/reports/s2_llm_batches_offline_readiness_v1.json"
OUT_MD = ROOT / "outputs/reports/s2_llm_batches_offline_readiness_v1.md"
SCRATCH = ROOT / "outputs/development/s2_llm_batches_offline_readiness_v1"

S2_12_STAGES = ("D-CAL", "D-REST", "F-1", "F-2", "F-3")
S2_12_AUTH = {
    stage: ROOT / f"configs/s2_12_api_authorization_{stage}.json"
    for stage in S2_12_STAGES
}
GDPR_AUTH = ROOT / "configs/gdpr7_direct_llm_authorization_event_v1.json"
GDPR_CONTRACT = ROOT / "configs/ablations/gdpr7_direct_llm_execution_contract_v1.json"
GDPR_PREFLIGHT = ROOT / "outputs/reports/gdpr7_direct_llm_preflight_v1.json"
S2_12_PREFLIGHT = ROOT / "outputs/reports/s2_12_api_preflight_v1.json"
ENV_PRECHECK = SCRIPTS / "check_api_env_ready_v1.py"
S2_12_RUNNER = SCRIPTS / "run_s2_12_direct_llm_v1.py"
GDPR_RUNNER = SCRIPTS / "run_gdpr7_direct_llm_v1.py"
GDPR_PROMOTER = SCRIPTS / "promote_gdpr7_direct_llm_arm_v1.py"

EXPECTED_CALLS = {"s2_12_batch_a": 63, "gdpr7_batch_b": 74}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout.strip().splitlines()[-8:],
        "stderr_tail": proc.stderr.strip().splitlines()[-8:],
    }


def env_precheck() -> dict:
    result = _run([sys.executable, str(ENV_PRECHECK)])
    text = "\n".join(result["stdout_tail"] + result["stderr_tail"])
    missing = [line for line in text.splitlines() if line.startswith("FAIL")]
    result["ready"] = result["exit_code"] == 0
    result["missing_items"] = missing
    return result


def authorization_assets() -> dict:
    assets = {}
    for stage, path in S2_12_AUTH.items():
        assets[f"s2_12:{stage}"] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "exists": path.is_file(),
            "sha256": _sha(path) if path.is_file() else None,
        }
    for label, path in (("gdpr7:authorization", GDPR_AUTH),
                        ("gdpr7:contract", GDPR_CONTRACT),
                        ("gdpr7:preflight", GDPR_PREFLIGHT),
                        ("s2_12:preflight", S2_12_PREFLIGHT)):
        assets[label] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "exists": path.is_file(),
            "sha256": _sha(path) if path.is_file() else None,
        }
    return assets


def declared_call_counts() -> dict:
    out = {}
    if GDPR_PREFLIGHT.is_file():
        doc = _read(GDPR_PREFLIGHT)
        calls = (doc.get("arms") or {}).get("direct_llm", {}).get("calls")
        out["gdpr7_batch_b"] = {
            "declared_calls": len(calls) if isinstance(calls, list) else calls,
            "source": "outputs/reports/gdpr7_direct_llm_preflight_v1.json",
        }
    if S2_12_PREFLIGHT.is_file():
        doc = _read(S2_12_PREFLIGHT)
        total = 0
        found = False
        for arm, block in (doc.get("arms") or {}).items():
            calls = block.get("calls") if isinstance(block, dict) else None
            if isinstance(calls, list):
                total += len(calls)
                found = True
        out["s2_12_batch_a"] = {
            "declared_calls": total if found else None,
            "source": "outputs/reports/s2_12_api_preflight_v1.json",
        }
    return out


def gdpr_fake_rehearsal() -> dict:
    raw = SCRATCH / "raw"
    capsule = SCRATCH / "capsule"
    for path in (raw, capsule):
        shutil.rmtree(path, ignore_errors=True)
    result = _run([sys.executable, str(GDPR_RUNNER), "--fake-transport",
                   "--raw-dir", str(raw.relative_to(ROOT)).replace("\\", "/"),
                   "--capsule-dir", str(capsule.relative_to(ROOT)).replace("\\", "/")])
    text = "\n".join(result["stdout_tail"])
    result["status_line"] = text.splitlines()[0] if text else ""
    result["completed_74"] = bool(re.search(r"completed=74", text))
    result["zero_calls"] = bool(re.search(r"cost_usd=0\.0", text))
    result["fake_capsule_dir"] = str(capsule.relative_to(ROOT)).replace("\\", "/")
    return result


def gdpr_real_refusal() -> dict:
    raw = SCRATCH / "raw_refuse"
    capsule = SCRATCH / "capsule_refuse"
    result = _run([sys.executable, str(GDPR_RUNNER),
                   "--raw-dir", str(raw.relative_to(ROOT)).replace("\\", "/"),
                   "--capsule-dir", str(capsule.relative_to(ROOT)).replace("\\", "/")])
    text = "\n".join(result["stdout_tail"] + result["stderr_tail"])
    result["refused"] = result["exit_code"] != 0 and "refus" in text.lower()
    return result


def promotion_refusal() -> dict:
    result = _run([sys.executable, str(GDPR_PROMOTER), "--capsule-dir",
                   str((SCRATCH / "capsule").relative_to(ROOT)).replace("\\", "/")])
    text = "\n".join(result["stdout_tail"] + result["stderr_tail"])
    result["refused"] = result["exit_code"] != 0
    result["refused_fake_capsule"] = "fake" in text.lower()
    return result


def s2_12_real_refusal() -> dict:
    result = _run([sys.executable, str(S2_12_RUNNER), "--transport", "real",
                   "--allow-llm", "--auth-file",
                   "configs/s2_12_api_authorization_D-CAL.json",
                   "--stage-id", "D-CAL",
                   "--output-dir", str((SCRATCH / "s212").relative_to(ROOT)).replace("\\", "/"),
                   "--raw-dir", str((SCRATCH / "s212_raw").relative_to(ROOT)).replace("\\", "/")])
    text = "\n".join(result["stdout_tail"] + result["stderr_tail"])
    result["refused"] = result["exit_code"] != 0
    result["reason"] = next((line for line in text.splitlines()
                             if "refused" in line.lower()), "")
    return result


def build_report() -> dict:
    precheck = env_precheck()
    assets = authorization_assets()
    calls = declared_call_counts()
    rehearsal = gdpr_fake_rehearsal()
    refusal = gdpr_real_refusal()
    promotion = promotion_refusal()
    s212 = s2_12_real_refusal()

    assets_ok = all(entry["exists"] for entry in assets.values())
    counts_ok = (
        calls.get("gdpr7_batch_b", {}).get("declared_calls") == EXPECTED_CALLS["gdpr7_batch_b"]
        and calls.get("s2_12_batch_a", {}).get("declared_calls") == EXPECTED_CALLS["s2_12_batch_a"]
    )
    chain_ok = (rehearsal["exit_code"] == 0 and rehearsal["completed_74"]
                and rehearsal["zero_calls"] and refusal["refused"]
                and promotion["refused"] and s212["refused"])

    return {
        "schema_version": "s2_llm_batches_offline_readiness@1.0.0",
        "report_id": "s2_llm_batches_offline_readiness_v1",
        "scope": "offline readiness only; no LLM/API call is made",
        "batches": {
            "s2_12_batch_a": {"declared_calls": 63,
                              "method": "direct_llm 36 + sun_llm_fallback 27",
                              "authorization": "authorized 2026-09-07 (off-peak, retry=0)"},
            "gdpr7_batch_b": {"declared_calls": 74,
                              "method": "direct_llm (GDPR scope gdpr7_direct_llm_v1:74)",
                              "authorization": "authorized 2026-09-07 (off-peak, retry=0)"},
        },
        "authorization_assets": assets,
        "authorization_assets_ok": assets_ok,
        "declared_call_counts": calls,
        "declared_call_counts_ok": counts_ok,
        "credential_precheck": precheck,
        "execution_chain": {
            "gdpr_fake_rehearsal": rehearsal,
            "gdpr_real_run_refusal_without_contract": refusal,
            "promotion_refusal_of_fake_capsule": promotion,
            "s2_12_real_run_refusal_without_credentials": s212,
            "chain_ok": chain_ok,
        },
        "blocker": {
            "blocked": not precheck["ready"],
            "reason": ("process-environment credentials absent; both runners read "
                       "only the process environment and never the project .env"),
            "missing_items": precheck["missing_items"],
            "unblock_command": "python formal_experiment/scripts/check_api_env_ready_v1.py",
            "required_env_keys": [
                "BPC_HYBRID_LLM_ENABLED=true",
                "BPC_HYBRID_LLM_PROVIDER=openai_compatible",
                "BPC_HYBRID_LLM_MODEL=deepseek-v4-pro",
                "BPC_HYBRID_LLM_BASE_URL=https://api.deepseek.com/v1",
                "BPC_HYBRID_LLM_API_KEY=<injected by the host, never committed>",
                "BPC_HYBRID_LLM_MAX_TOKENS=4096",
                "BPC_HYBRID_LLM_TEMPERATURE=0",
                "BPC_HYBRID_LLM_TOP_P=1",
            ],
            "run_commands": {
                "s2_12_batch_a": (
                    "python scripts/run_s2_12_direct_llm_v1.py --transport real "
                    "--allow-llm --auth-file configs/s2_12_api_authorization_D-CAL.json "
                    "--stage-id D-CAL --output-dir outputs/development/s2_12_direct_llm_stage_dcal_v1 "
                    "--raw-dir outputs/development/s2_12_direct_llm_raw_dcal_v1"),
                "gdpr7_batch_b": (
                    "python scripts/run_gdpr7_direct_llm_v1.py "
                    "--contract-file configs/ablations/gdpr7_direct_llm_execution_contract_v1.json "
                    "--authorization-file configs/gdpr7_direct_llm_authorization_event_v1.json "
                    "--raw-dir outputs/development/gdpr7_direct_llm_raw_real_v1 "
                    "--capsule-dir outputs/development/gdpr7_direct_llm_real_v1"),
                "gdpr7_promotion": (
                    "python scripts/promote_gdpr7_direct_llm_arm_v1.py --apply"),
            },
        },
        "conclusion": {
            "offline_preparation_complete": bool(assets_ok and counts_ok and chain_ok),
            "real_calls_made": 0,
            "real_calls_remaining": 137,
            "blocked_on": "process-environment credentials" if not precheck["ready"] else None,
            "claim_boundary": (
                "No S2.12 / GDPR real-LLM result exists yet; the LLM-SE GDPR arm "
                "capsule data/predictions/gdpr7_direct_llm_v1 does not exist, so the "
                "downstream LLM-vs-rules Stage-3 comparison cannot be run on real "
                "LLM-SE predictions."),
        },
        "zero_api": {"new_llm_api_calls": 0},
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# 真实 LLM 对照批次：离线就绪报告（零 API）",
        "",
        f"**报告**：`{report['report_id']}`",
        "",
        "## 批次",
        "",
        "| 批次 | 声明调用数 | 方法 | 授权 |",
        "|---|---:|---|---|",
    ]
    for name, block in report["batches"].items():
        lines.append(f"| {name} | {block['declared_calls']} | {block['method']} | "
                     f"{block['authorization']} |")
    lines += [
        "",
        "## 离线检查",
        "",
        "| 检查 | 结果 |",
        "|---|---|",
        f"| 授权/合同/预检资产齐备 | {report['authorization_assets_ok']} |",
        f"| 声明调用数与预检一致 | {report['declared_call_counts_ok']} |",
        f"| GDPR 74 次假传输全流程 | "
        f"{report['execution_chain']['gdpr_fake_rehearsal']['completed_74']} |",
        f"| 假传输零计费 | "
        f"{report['execution_chain']['gdpr_fake_rehearsal']['zero_calls']} |",
        f"| 无合同文件时真实运行被拒 | "
        f"{report['execution_chain']['gdpr_real_run_refusal_without_contract']['refused']} |",
        f"| 假胶囊被 promotion 拒绝 | "
        f"{report['execution_chain']['promotion_refusal_of_fake_capsule']['refused']} |",
        f"| 无凭据时 S2.12 真实运行被拒 | "
        f"{report['execution_chain']['s2_12_real_run_refusal_without_credentials']['refused']} |",
        "",
        "## 阻塞",
        "",
        f"- 是否阻塞：**{report['blocker']['blocked']}**",
        f"- 原因：{report['blocker']['reason']}",
        "",
        "缺失项：",
        "",
    ]
    for item in report["blocker"]["missing_items"]:
        lines.append(f"- `{item}`")
    lines += [
        "",
        "## 结论",
        "",
        f"- 离线准备完成：**{report['conclusion']['offline_preparation_complete']}**",
        f"- 真实调用已发生：{report['conclusion']['real_calls_made']}",
        f"- 剩余真实调用：{report['conclusion']['real_calls_remaining']}",
        f"- 阻塞于：{report['conclusion']['blocked_on']}",
        "",
        f"> {report['conclusion']['claim_boundary']}",
        "",
        "零 LLM/API/网络；未写入 `data/`。",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report()
    if args.check:
        if not OUT_JSON.is_file():
            print(json.dumps({"mode": "check", "valid": False,
                              "reason": "report missing"}, ensure_ascii=False))
            return 2
        same = json.dumps(_read(OUT_JSON), ensure_ascii=False, sort_keys=True) == \
            json.dumps(report, ensure_ascii=False, sort_keys=True)
        print(json.dumps({"mode": "check", "valid": same}, ensure_ascii=False))
        return 0 if same else 2

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n")
                         .encode("utf-8"))
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({
        "offline_preparation_complete":
            report["conclusion"]["offline_preparation_complete"],
        "blocked": report["blocker"]["blocked"],
        "missing_items": report["blocker"]["missing_items"],
        "report": str(OUT_JSON.relative_to(ROOT)).replace("\\", "/"),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
