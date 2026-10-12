"""生成面向人和 Agent 的中文逐文件目录。

脚本只枚举活动路径，不读取文件内容；跳过归档、.env 与可再生缓存。
"""

from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "FILE_CATALOG.md"
IGNORED_DIRS = {".pytest_cache", "__pycache__", ".tmp", "_retired"}
IGNORED_FILES = {".env"}
IGNORED_SUFFIXES = {".bak"}


def _status(path: Path) -> str:
    parts = path.parts
    if parts[0] == "_retired":
        return "退役归档"
    if parts[0] == "data" and len(parts) > 1 and parts[1] == "development":
        return "开发/溯源"
    if parts[0] == "data" and len(parts) > 1:
        return "正式区（受门禁）"
    if parts[:2] == ("docs", "research"):
        return "研究证据"
    if path.name == ".gitkeep":
        return "目录占位"
    return "活动"


def _role(path: Path) -> str:
    name = path.name
    suffix = path.suffix.lower()
    explicit = {
        "AGENTS.md": "Agent 强制合同与操作边界",
        "README.md": "所在目录的入口说明",
        "MANIFEST.md": "结构或迁移清单",
        "MASTER_PIPELINE.md": "唯一完整三个部分路线与任务树",
        "PROJECT_AUDIT.md": "唯一实时项目状态（兼容文件名）",
        "AGENT_RUNBOOK.md": "Agent 按任务依赖派工规则与可复制 Prompt",
        "DIRECTORY_GUIDE.md": "中文目录职责地图",
        "FILE_CATALOG.md": "自动生成的逐文件目录",
        "EXPERIMENT_LOG.md": "中文人类可读实验日志",
        "EXPERIMENT_EVENTS.jsonl": "追加式机器实验事件",
        "THESIS_DRAFT.md": "中文论文连续工作稿与结果占位",
        "CLAIM_EVIDENCE_MATRIX.md": "科学主张、证据状态和解锁条件",
        "AI_CHANGE_PROTOCOL.md": "实验日志与自动检查协议",
        "audit_project.py": "离线项目完整性检查（兼容文件名）",
        "record_change.py": "追加经过验证的变更/运行/里程碑事件",
        "generate_file_catalog.py": "重建本逐文件目录",
        ".gitkeep": "保留当前空目录",
    }
    if name in explicit:
        return explicit[name]
    if suffix == ".py":
        return "Python 实现、脚本或测试"
    if suffix == ".md":
        return "说明、规范或研究文档"
    if suffix in {".json", ".jsonl"}:
        return "机器可读配置、数据、事件或产物"
    if suffix in {".yaml", ".yml", ".toml"}:
        return "配置或工程元数据"
    if suffix in {".bpmn", ".xml"}:
        return "流程模型或测试 fixture"
    if suffix in {".svg", ".html"}:
        return "历史可视化或报告"
    if suffix == ".txt":
        return "文本清单或依赖说明"
    if suffix == ".example":
        return "不含密钥的配置示例"
    return "项目文件"


def collect_files() -> list[Path]:
    """Return tracked and non-ignored untracked files in the formal capsule.

    The workspace may contain large ignored development runs and local review
    backups.  A reproducible catalog must not change merely because those
    machine-local artifacts exist. Retired provenance is excluded even when
    tracked: it must never be discovered as an active review batch.
    """
    files: list[Path] = []
    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            ROOT.name,
        ],
        cwd=ROOT.parent,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    for item in completed.stdout.splitlines():
        path = ROOT.parent / item
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.name in IGNORED_FILES:
            continue
        if relative.suffix.lower() in IGNORED_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        files.append(relative)
    return sorted(files, key=lambda item: item.as_posix().lower())


def render(files: list[Path]) -> str:
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        groups[path.parts[0]].append(path)
    lines = [
        "# 项目逐文件目录",
        "",
        f"**生成日期**：{date.today().isoformat()}",
        f"**收录文件**：{len(files)} 个（不含 `_retired/`、Git-ignored 本地产物、`.env` 与可再生缓存）",
        "**生成命令**：`python formal_experiment/scripts/generate_file_catalog.py`",
        "",
        "本文件只收录活动项目文件；归档仅在明确追溯时查阅，不进入默认目录。",
        "“开发/溯源”表示不能直接用于最终论文表格；“正式区（受门禁）”",
        "表示只有冻结和运行门禁通过后才能写入。",
        "",
    ]
    for group in sorted(groups, key=str.lower):
        lines.extend([
            f"## `{group}`",
            "",
            "| 文件 | 状态 | 用途 |",
            "|---|---|---|",
        ])
        for path in groups[group]:
            display = path.as_posix().replace("|", "\\|")
            lines.append(f"| `{display}` | {_status(path)} | {_role(path)} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查目录是否与当前文件集合一致，不写文件。",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    if output != DEFAULT_OUTPUT.resolve():
        raise SystemExit("目录只能写入 docs/FILE_CATALOG.md")
    files = collect_files()
    relative_output = output.relative_to(ROOT)
    if relative_output not in files:
        files.append(relative_output)
        files.sort(key=lambda item: item.as_posix().lower())
    expected = render(files)
    if args.check:
        try:
            current = output.read_text(encoding="utf-8")
        except FileNotFoundError:
            print("逐文件目录不存在，请先运行生成命令。")
            return 1
        if current != expected:
            print("逐文件目录已过期，请重新运行生成命令。")
            return 1
        print(f"逐文件目录有效，共收录 {len(files)} 个文件。")
        return 0
    output.write_text(expected, encoding="utf-8")
    print(f"已生成 {output}，收录 {len(files)} 个文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
