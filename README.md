# LLM4BPC workspace

The workspace is intentionally split into three areas:

```text
formal_experiment/   active, audited, reproducible experiment
references/          papers, external source code, datasets, and tools
archive/             historical rounds, outputs, caches, and unused material
```

Only `formal_experiment/` is active experiment code. Start with:

- `formal_experiment/docs/MASTER_PIPELINE.md`
- `formal_experiment/docs/PROJECT_AUDIT.md`
- `formal_experiment/README.md`
- `formal_experiment/AGENTS.md`

For experiment-affecting code/config/data changes, the quick integrity check is:

```powershell
python formal_experiment/scripts/audit_project.py
```

PPT, prose, formatting, and other artifact-only work uses content/render/file
checks instead. Code changes default to named relevant tests. Full tests
(`--with-tests` or equivalent) require explicit user authorization for this
task and an expected duration; finishing, logging, committing, and pushing do
not trigger them. See the root `AGENTS.md` and
`formal_experiment/docs/AI_CHANGE_PROTOCOL.md` for the scope policy.

Experiment-affecting changes use `formal_experiment/scripts/record_change.py`
with explicit `--test-target` files or an already matching full-test receipt.
Without either, it starts no tests and writes no event. Artifact-only changes
may use their scoped Git commit as the record. Safety declarations and Gold/
API/formal-release gates remain in force.

`references/` and `archive/` are retained for provenance. They must not be
imported by formal code or used as current experimental evidence.

The hidden `.agents/` and `.pytest_cache/` directories are tool-managed empty
workspace state and are not part of the experiment.
