# -*- coding: utf-8 -*-
"""R1 global role-candidate artifact for the Winter native baseline.

Reads only the blinded inference-view BPMN paths and extracts ``process@name``
values.  It must not read the construction reference, an error/mutation type,
control/pair/family metadata, or any role-to-case/activity mapping.
"""

from __future__ import annotations

import hashlib
import xml.dom.minidom as minidom
from pathlib import Path
from typing import Any, Mapping


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_global_role_candidates(inference_view: Mapping[str, Any],
                                   root: Path) -> dict[str, Any]:
    roles: set[str] = set()
    sources: dict[str, str] = {}
    for raw in inference_view.get("items") or []:
        rel = str(raw.get("bpmn_path") or "")
        if not rel:
            raise ValueError("inference item missing bpmn_path")
        path = root / rel
        if not path.is_file():
            raise ValueError(f"inference BPMN missing: {rel}")
        doc = minidom.parse(str(path))
        names: list[str] = []
        for process in doc.getElementsByTagName("process"):
            name = process.getAttribute("name").strip()
            if name:
                names.append(name)
                roles.add(name.lower())
        sources[rel] = _sha_file(path)
        if not names:
            # The R1 contract says to ignore empty names; a file with no
            # process name still gets its hash bound so drift is visible.
            sources[rel] = _sha_file(path)
    return {
        "schema_version": "stage3_winter_global_role_candidates@1.0.0",
        "source": "inference_view items only",
        "normalization": "lower/strip unique",
        "role_count": len(roles),
        "roles": sorted(roles),
        "model_sources": dict(sorted(sources.items())),
        "forbidden_inputs": [
            "construction_reference.json",
            "error/mutation type",
            "pair/control/family metadata",
            "role-to-case/activity mapping",
        ],
    }


__all__ = ["collect_global_role_candidates"]
