"""六家 Stage 2 模型的离线预检与授权运行入口；默认不读取密钥、不联网。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bpc_hybrid import multi_model_stage2 as models


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init-env", help="只追加空白密钥项；不读取已有 .env")
    sub.add_parser("list", help="列出模型与密钥变量名；不读取 .env")
    plan = sub.add_parser("plan", help="生成请求计划和未授权模板；零 API")
    plan.add_argument("--providers", required=True, help="qwen,mimo,kimi,grok,glm,minimax 或 all")
    plan.add_argument("--samples", type=int, default=20)
    plan.add_argument("--run-id", required=True)
    run = sub.add_parser("run", help="仅在本次授权后执行；不自动重试")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--authorization", type=Path, required=True)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--allow-llm", action="store_true")
    run.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "init-env":
            print(models.init_env())
        elif args.command in {None, "list"}:
            for name, profile in models.load_catalog()["profiles"].items():
                print(f"{name:8} {profile['display_name']:8} {profile['model']}  {profile['api_key_env']}")
            print("离线模式；密钥未读取，API 调用 0。")
        elif args.command == "plan":
            providers = list(models.load_catalog()["profiles"]) if args.providers == "all" else args.providers.split(",")
            providers = [p.strip() for p in providers]
            value = models.build_plan(providers, args.samples, args.run_id)
            directory = models.RUNS / args.run_id
            if directory.exists():
                raise models.ModelRunError("run_id 目录已存在；请选择新的 ID，不覆盖旧计划。")
            models.write_json(directory / "plan.json", value, exclusive=True)
            models.write_json(directory / "authorization.template.json", models.authorization_template(value), exclusive=True)
            print(f"离线预检完成：{len(providers)} 家 × {args.samples} 条 = {value['planned_calls']} 次计划调用。")
            print(f"计划：{directory / 'plan.json'}")
            print("授权状态：false；价格和费用上限待核对；实际 API 调用 0。")
        elif args.command == "run":
            if not args.execute or not args.allow_llm:
                raise models.ModelRunError("未提供 --execute 和 --allow-llm；不会读取密钥或调用 API。")
            result = models.execute_plan(models.read_json(args.plan), models.read_json(args.authorization),
                                         execute=args.execute, allow_llm=args.allow_llm, resume=args.resume)
            print(json.dumps({"run_id": result["run_id"], "status": result["status"],
                              "llm_calls": result["llm_calls"], "valid_predictions": result["valid_predictions"]}, ensure_ascii=False))
            return 0 if result["status"] == "succeeded" else 2
        return 0
    except models.ModelRunError as exc:
        print(f"已停止：{exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError):
        print("已停止：文件、目录或配置不合法；不输出敏感内容。", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
