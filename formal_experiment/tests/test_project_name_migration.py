"""Offline migration tests using synthetic names and evidence only."""
import io
import json
import zipfile

import migrate_project_names as migration


def names():
    return migration.Names('legacy-demo', 'legacy_demo', 'LEGACY_DEMO')


def test_names_preserve_bytes_and_distinguish_code_and_brand():
    original = b'import legacy_demo.api\r\n# LEGACY_DEMO_KEY legacy-demo\r\n'
    assert names().data(original) == b'import llm4bpc.api\r\n# LLM4BPC_KEY LLM4BPC\r\n'
    assert names().data(b'\x00legacy_demo\xff') == b'\x00legacy_demo\xff'
    assert names().text('legacy%2Ddemo') == 'LLM4BPC'


def test_archive_only_changes_named_text_and_keeps_other_members():
    source = io.BytesIO()
    with zipfile.ZipFile(source, 'w') as z:
        z.writestr('docs/legacy-demo.xml', b'<title>legacy-demo</title>')
        z.writestr('media/image.bin', b'\x00legacy_demo\xff')
    updated, changed = migration.translate_zip(source.getvalue(), names())
    assert changed == 1
    with zipfile.ZipFile(io.BytesIO(updated)) as z:
        assert z.read('docs/LLM4BPC.xml') == b'<title>LLM4BPC</title>'
        assert z.read('media/image.bin') == b'\x00legacy_demo\xff'


def test_archive_with_secret_member_is_not_opened_for_content(monkeypatch):
    source = io.BytesIO()
    with zipfile.ZipFile(source, 'w') as z:
        z.writestr('.env', b'synthetic-fixture-only')
        z.writestr('readme.md', b'legacy-demo')
    monkeypatch.setattr(zipfile.ZipFile, 'read', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('member read forbidden')))
    assert migration.translate_zip(source.getvalue(), names()) == (source.getvalue(), 0)


def test_plan_backs_up_originals_without_mutating_or_reading_secrets(tmp_path, monkeypatch):
    source = tmp_path / 'formal_experiment/src/legacy_demo/module.py'
    source.parent.mkdir(parents=True)
    original = b'import legacy_demo\r\n'
    source.write_bytes(original)
    protected = tmp_path / 'formal_experiment/.env'
    protected.write_bytes(b'synthetic-fixture-only')
    from pathlib import Path
    original_read = Path.read_bytes
    def guarded_read(path):
        assert path != protected, 'project secret must not be read'
        return original_read(path)
    monkeypatch.setattr(Path, 'read_bytes', guarded_read)
    monkeypatch.setattr(migration.subprocess, 'check_output', lambda *args, **kwargs: 'a' * 40)
    backup = tmp_path / 'formal_experiment/.tmp/name-migration'
    payload = migration.plan(tmp_path, backup, names())
    assert source.read_bytes() == original
    assert len(payload['files']) == 1
    assert (backup / 'staged/formal_experiment/src/llm4bpc/module.py').read_bytes() == b'import llm4bpc\r\n'
    with zipfile.ZipFile(backup / 'original_files.zip') as z:
        assert z.namelist() == ['formal_experiment/src/legacy_demo/module.py']
        assert z.read(z.namelist()[0]) == original
    assert json.loads((backup / 'plan.json').read_text())['files'][0]['before_sha256'] == migration.digest(original)
