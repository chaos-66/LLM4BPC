"""Run native spaCy Winter without loading the optional PyTorch DLL.

The CPU en_core_web_sm pipeline uses Thinc/NumPy. Marking optional torch as
unavailable takes Thinc's normal ImportError fallback; no blocked DLL is run
and no package or operating-system security setting is changed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_stage3_winter_paper_rerun_v1 as replay


def configure_cpu() -> None:
    if "torch" in sys.modules and sys.modules["torch"] is not None:
        raise RuntimeError("CPU launcher must start before torch is loaded")
    sys.modules["torch"] = None


def main() -> int:
    configure_cpu()
    result = replay.infer()
    core = replay.read(replay.OUT / "run_manifest.json")
    manifest = dict(core)
    manifest["command"] = "python formal_experiment/scripts/run_stage3_winter_cpu_v1.py"
    manifest["core_run_manifest_sha256"] = replay.sha(replay.OUT / "run_manifest.json")
    manifest["runtime_launcher_sha256"] = replay.sha(Path(__file__))
    manifest["runtime_policy"] = "Optional torch unavailable; native en_core_web_sm Thinc/NumPy CPU pipeline."
    manifest["preflight_failures"] = [
        "Canonical source raw SHA differs only in CRLF/LF; canonical LF SHA matches original freeze.",
        "Evaluator source copy had one extra trailing blank line; removed before input freeze.",
        "Default spaCy import aborted on optional torch DLL WinError 4551 before predictions or output directory existed."
    ]
    replay.write(replay.OUT / "execution_manifest.json", manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
