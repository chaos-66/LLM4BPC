"""Plan a byte-preserving, backed-up project-name migration (offline only).

The caller supplies the source names. Original evidence and rename plans stay
in an ignored local backup. This tool does not alter Git history, credentials,
test receipts, numerical results, or execute any experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

TEXT_SUFFIXES = {'.py', '.pyi', '.md', '.txt', '.json', '.jsonl', '.toml', '.yaml', '.yml', '.ini', '.cfg', '.xml', '.bpmn', '.html', '.css', '.js', '.ts', '.java', '.sh', '.ps1', '.cmd', '.bat', '.csv', '.tsv', '.ipynb', '.log', '.diff', '.bak', '.body', '.iml', '.code-workspace', '.rst', '.tex', '.bib'}
ZIP_SUFFIXES = {'.zip', '.pptx', '.docx', '.xlsx'}
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.tmp', '.venv', 'venv', 'env', 'node_modules', 'site-packages'}
TEXT_NAMES = {'.gitattributes', '.gitignore', '.ignore', 'Makefile', 'Dockerfile', 'PKG-INFO', 'METADATA'}
HEX = re.compile(rb'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sensitive(path: Path) -> bool:
    return path.name.startswith('.env') or path.suffix.lower() in {'.key', '.pem', '.pfx', '.p12'}


def decode(data: bytes) -> tuple[str, str] | None:
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16'), 'utf-16'
    if b'\0' in data:
        return None
    try:
        return data.decode('utf-8'), 'utf-8'
    except UnicodeDecodeError:
        return None


class Names:
    def __init__(self, source_project: str, source_package: str, source_env: str):
        self.source_project = source_project
        self.source_package = source_package
        self.source_env = source_env
        self.pattern = re.compile('|'.join(re.escape(value) for value in (source_project, source_package, source_env)), re.I)

    def text(self, value: str) -> str:
        def replacement(match):
            old = match.group()
            return 'llm4bpc' if old == self.source_package else 'LLM4BPC'
        value = self.pattern.sub(replacement, value)
        return re.sub(re.escape(self.source_project).replace(r'\-', r'%2[dD]'), 'LLM4BPC', value, flags=re.I)

    def data(self, data: bytes) -> bytes:
        decoded = decode(data)
        if decoded is None:
            return data
        value, encoding = decoded
        updated = self.text(value)
        return data if updated == value else updated.encode(encoding)


def files_in(root: Path):
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS and not name.startswith(('.codex_worktree', '.tmp_', '.tmp-', 'name_migration_originals_')) and not (Path(base) / name).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            if path.is_symlink() or sensitive(path) or path.name == '.git':
                continue
            yield path


def translate_zip(data: bytes, names: Names) -> tuple[bytes, int]:
    source = io.BytesIO(data)
    output = io.BytesIO()
    changed = 0
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, 'w') as target:
        total = sum(info.file_size for info in original.infolist())
        if total > 512 * 1024 * 1024 or any(sensitive(Path(info.filename)) for info in original.infolist()):
            return data, 0
        seen = set()
        for info in original.infolist():
            new_name = names.text(info.filename)
            if new_name in seen:
                raise ValueError(f'Archive member collision: {new_name}')
            seen.add(new_name)
            member = original.read(info)
            updated = member
            member_path = Path(info.filename)
            if not sensitive(member_path) and (member_path.suffix.lower() in TEXT_SUFFIXES or member_path.name in TEXT_NAMES):
                updated = names.data(member)
            if updated != member or new_name != info.filename:
                changed += 1
            info.filename = new_name
            target.writestr(info, updated)
    return (output.getvalue(), changed) if changed else (data, 0)


def plan(root: Path, backup: Path, names: Names) -> dict:
    root = root.resolve()
    backup = backup.resolve()
    backup.relative_to(root / 'formal_experiment/.tmp')
    backup.mkdir(parents=True, exist_ok=False)
    staged = backup / 'staged'
    staged.mkdir()
    rows = []
    skipped_binary = []
    total_text = 0
    with zipfile.ZipFile(backup / 'original_files.zip', 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as original:
        for path in files_in(root):
            relative = path.relative_to(root).as_posix()
            target_name = names.text(relative)
            suffix = path.suffix.lower()
            is_text = suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES
            is_zip = suffix in ZIP_SUFFIXES
            if not (is_text or is_zip or relative != target_name):
                continue
            data = path.read_bytes()
            updated = data
            archive_members = 0
            if is_zip:
                try:
                    updated, archive_members = translate_zip(data, names)
                except zipfile.BadZipFile:
                    skipped_binary.append(relative)
            elif is_text:
                updated = names.data(data)
                total_text += 1
            if data == updated and relative == target_name:
                continue
            destination = root / target_name
            destination.resolve().relative_to(root)
            if destination.exists() and destination != path:
                raise ValueError(f'Destination already exists: {target_name}')
            original.writestr(relative, data)
            output = staged / target_name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(updated)
            rows.append({'source': relative, 'target': target_name, 'before_sha256': digest(data), 'after_sha256': digest(updated), 'before_bytes': len(data), 'after_bytes': len(updated), 'archive_members_changed': archive_members})
    payload = {'schema_version': 1, 'workspace': str(root), 'source_names': vars(names) | {'pattern': names.pattern.pattern}, 'original_git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, encoding='utf-8').strip(), 'text_files_scanned': total_text, 'files': rows, 'unreadable_archives': skipped_binary}
    (backup / 'plan.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    with zipfile.ZipFile(backup / 'original_files.zip') as original:
        assert original.testzip() is None
        for row in rows:
            assert digest(original.read(row['source'])) == row['before_sha256']
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--source-project', required=True)
    parser.add_argument('--source-package', required=True)
    parser.add_argument('--source-env', required=True)
    args = parser.parse_args()
    result = plan(args.workspace, args.backup, Names(args.source_project, args.source_package, args.source_env))
    print(json.dumps({'planned_files': len(result['files']), 'text_files_scanned': result['text_files_scanned'], 'original_bytes': sum(row['before_bytes'] for row in result['files']), 'renamed_paths': sum(row['source'] != row['target'] for row in result['files']), 'archive_members_changed': sum(row['archive_members_changed'] for row in result['files']), 'backup_verified': True}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
