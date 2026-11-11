# -*- coding: utf-8 -*-
"""Shared semantic matcher v2 for Stage 3-v2.

This module replaces method-specific / historical spaCy similarity calls with
one deterministic, shared similarity interface.  It does not read Gold,
reference labels, target activities, mutation metadata, or model predictions.

Backends
--------
* ``spacy_en_core_web_md``: locally installed spaCy vector model.  Similarity
  is cosine between averaged document vectors, clamped to ``[0, 1]``.
* ``spacy_en_core_web_sm``: preserved local baseline behaviour.  Similarity is
  ``Doc.similarity`` (spaCy tagger/parser tensor similarity for the small
  model), clamped to ``[0, 1]``.
* Sentence-Transformer candidates are recognised only when the package and a
  local model snapshot are already present.  No download is attempted.

The matcher is stateful only for an in-process deterministic cache.  Batch
ordering cannot affect a score because every score is computed per text pair.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import unicodedata
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "stage3_v2_semantic_matcher@1.0.0"
DEFAULT_CACHE_SIZE = 262_144

# Backend short names are deliberately stable identifiers used in freeze
# manifests and reports.
SPACY_MD = "spacy_en_core_web_md"
SPACY_SM = "spacy_en_core_web_sm"
ST_MPNET = "sentence_transformers_all_mpnet_base_v2"
ST_MINILM = "sentence_transformers_all_minilm_l6_v2"

CANDIDATE_SHORT_NAMES = (SPACY_MD, SPACY_SM, ST_MPNET, ST_MINILM)

_SPACE_RE = re.compile(r"\s+", flags=re.UNICODE)


class SemanticMatcherError(RuntimeError):
    """Base error for Stage 3-v2 semantic matching."""


class BackendUnavailableError(SemanticMatcherError):
    """Requested semantic backend is not available without a download."""


def normalize_text_v2(text: str) -> str:
    """Apply the pre-registered light, general normalization policy.

    Allowed operations only: Unicode NFKC normalization, NBSP replacement,
    strip, whitespace collapse, and case folding.  No synonym dictionaries,
    domain rewrites, Gold-derived rewrites, or method-specific normalization
    are permitted.
    """
    if text is None:
        return ""
    value = unicodedata.normalize("NFKC", str(text))
    value = value.replace("\u00a0", " ")
    value = _SPACE_RE.sub(" ", value).strip()
    return value.casefold()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class SpacySimilarityBackend:
    """Locally loaded spaCy backend.

    The ``mode`` value is recorded in the identity manifest.  ``md_vector``
    computes an explicit cosine over averaged document vectors; ``sm_baseline``
    preserves the historical ``Doc.similarity`` behaviour.
    """

    kind = "spacy"

    def __init__(self, model_name: str):
        try:
            import spacy
        except ImportError as exc:  # pragma: no cover - environment guard
            raise BackendUnavailableError("spaCy is not installed") from exc
        installed = set(spacy.util.get_installed_models())
        if model_name not in installed:
            raise BackendUnavailableError(
                f"spaCy model {model_name!r} is not installed locally"
            )
        self.model_name = model_name
        self.nlp = spacy.load(model_name)
        self.short_name = SPACY_MD if model_name == "en_core_web_md" else SPACY_SM
        self.mode = "md_vector_cosine" if model_name == "en_core_web_md" else "sm_text_similarity"
        self._doc_cache: "OrderedDict[str, Any]" = OrderedDict()
        self._doc_cache_limit = 65_536
        meta = dict(getattr(self.nlp, "meta", {}) or {})
        self.model_meta = {
            "name": meta.get("name"),
            "version": meta.get("version"),
            "description": meta.get("description"),
            "vectors_length": int(getattr(self.nlp.vocab, "vectors_length", 0) or 0),
        }
        model_path = None
        try:
            model_path = Path(str(getattr(self.nlp, "path", "") or "")).resolve()
        except Exception:  # noqa: BLE001
            model_path = None
        self.model_path = str(model_path) if model_path else None
        self.artifact_hash = None
        if model_path and model_path.exists():
            # Meta hash is small and stable; full vector-table hashing would be
            # expensive but can be added without changing the interface.
            self.artifact_hash = _sha256_file(model_path / "meta.json")

    def identity(self) -> dict[str, Any]:
        return {
            "short_name": self.short_name,
            "kind": self.kind,
            "model_name": self.model_name,
            "mode": self.mode,
            "model_meta": self.model_meta,
            "model_path": self.model_path,
            "artifact_meta_sha256": self.artifact_hash,
            "backend_identity_sha256": _json_hash({
                "short_name": self.short_name,
                "model_name": self.model_name,
                "mode": self.mode,
                "model_meta": self.model_meta,
                "artifact_meta_sha256": self.artifact_hash,
            }),
        }

    def _doc(self, normalized_text: str) -> Any:
        doc = self._doc_cache.get(normalized_text)
        if doc is None:
            doc = self.nlp(normalized_text)
            self._doc_cache[normalized_text] = doc
            if len(self._doc_cache) > self._doc_cache_limit:
                self._doc_cache.popitem(last=False)
        else:
            self._doc_cache.move_to_end(normalized_text)
        return doc

    def similarity(self, left: str, right: str) -> float:
        left_norm = normalize_text_v2(left)
        right_norm = normalize_text_v2(right)
        if left_norm == right_norm:
            return 1.0
        left_doc = self._doc(left_norm)
        right_doc = self._doc(right_norm)
        if self.mode == "sm_text_similarity":
            try:
                value = float(left_doc.similarity(right_doc))
            except Exception:  # noqa: BLE001 - keep checker usable
                value = 0.0
        else:
            try:
                left_norm_value = float(left_doc.vector_norm)
                right_norm_value = float(right_doc.vector_norm)
                if left_norm_value <= 0.0 or right_norm_value <= 0.0:
                    return 0.0
                dot = float(left_doc.vector @ right_doc.vector)
                value = dot / (left_norm_value * right_norm_value)
            except Exception:  # noqa: BLE001
                value = 0.0
        if not math.isfinite(value):
            return 0.0
        return max(0.0, min(1.0, value))


class SentenceTransformerBackend:
    """Optional local SentenceTransformer backend; never downloads a model."""

    kind = "sentence_transformers"

    def __init__(self, short_name: str, model_path: str | Path):
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise BackendUnavailableError("sentence-transformers is not installed") from exc
        self.short_name = short_name
        self.model_name = str(model_path)
        self.model = SentenceTransformer(str(model_path), device="cpu", local_files_only=True)
        self.model.eval()
        self._cache: "OrderedDict[str, Any]" = OrderedDict()
        self._cache_limit = 32_768
        self.vector_dim = int(self.model.get_sentence_embedding_dimension() or 0)
        self.model_path = str(Path(model_path).resolve())
        self.artifact_hash = None

    def identity(self) -> dict[str, Any]:
        return {
            "short_name": self.short_name,
            "kind": self.kind,
            "model_name": self.model_name,
            "mode": "sentence_embedding_cosine",
            "vector_dim": self.vector_dim,
            "model_path": self.model_path,
            "backend_identity_sha256": _json_hash({
                "short_name": self.short_name,
                "kind": self.kind,
                "model_name": self.model_name,
                "vector_dim": self.vector_dim,
            }),
        }

    def _embed(self, normalized_text: str) -> Any:
        import numpy as np
        vec = self._cache.get(normalized_text)
        if vec is None:
            vec = self.model.encode(
                [normalized_text],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )[0]
            self._cache[normalized_text] = vec
            if len(self._cache) > self._cache_limit:
                self._cache.popitem(last=False)
        else:
            self._cache.move_to_end(normalized_text)
        return np.asarray(vec, dtype="float32")

    def similarity(self, left: str, right: str) -> float:
        left_norm = normalize_text_v2(left)
        right_norm = normalize_text_v2(right)
        if left_norm == right_norm:
            return 1.0
        import numpy as np
        a = self._embed(left_norm)
        b = self._embed(right_norm)
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom <= 0.0:
            return 0.0
        value = float(np.dot(a, b) / denom)
        if not math.isfinite(value):
            return 0.0
        return max(0.0, min(1.0, value))


class SharedSemanticMatcherV2:
    """One shared matcher for Sun and Ours.

    The public API is deliberately small::

        matcher.similarity(text_a, text_b) -> float
        matcher.text_pair(text_a, text_b) -> float
        matcher.identity() -> dict

    The matcher uses a deterministic cache keyed by backend identity and the
    two normalized texts.  It does not retain cross-case state.
    """

    schema_version = SCHEMA_VERSION

    def __init__(self, backend: SpacySimilarityBackend | SentenceTransformerBackend,
                 *, cache_size: int = DEFAULT_CACHE_SIZE):
        self.backend = backend
        self.cache_size = int(cache_size)
        self._cache: "OrderedDict[tuple[str, str, str], float]" = OrderedDict()
        self._identity = backend.identity()
        self._identity_sha = str(self._identity.get("backend_identity_sha256") or "")
        self._cache_hits = 0
        self._cache_misses = 0

    # ------------------------------------------------------------- constructors
    @classmethod
    def for_backend(cls, short_name: str, *, cache_size: int = DEFAULT_CACHE_SIZE) -> "SharedSemanticMatcherV2":
        backend = load_backend(short_name)
        return cls(backend, cache_size=cache_size)

    # ---------------------------------------------------------------- public API
    def similarity(self, text_a: str, text_b: str) -> float:
        a = normalize_text_v2(text_a)
        b = normalize_text_v2(text_b)
        if a == b:
            return 1.0
        # Cache both orientations to make symmetry explicit and to avoid
        # duplicate work if callers reverse arguments.
        cache_key = (self._identity_sha, a, b)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._cache_hits += 1
            return cached
        reverse_key = (self._identity_sha, b, a)
        cached = self._cache.get(reverse_key)
        if cached is not None:
            self._cache_hits += 1
            return cached
        value = float(self.backend.similarity(a, b))
        if not math.isfinite(value):
            value = 0.0
        value = max(0.0, min(1.0, value))
        self._cache_misses += 1
        self._cache[cache_key] = value
        if len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)
        return value

    def text_pair(self, text_a: str, text_b: str) -> float:
        """Compatibility shim for the frozen SunScorer interface."""
        return self.similarity(text_a, text_b)

    def similarity_many(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        """Compute scores in the supplied order; no batch-dependent state."""
        return [self.similarity(a, b) for a, b in pairs]

    def identity(self) -> dict[str, Any]:
        return dict(self._identity)

    def stats(self) -> dict[str, int]:
        return {
            "cache_hits": int(self._cache_hits),
            "cache_misses": int(self._cache_misses),
            "cache_size": len(self._cache),
        }


def _spacy_installed_models() -> set[str]:
    try:
        import spacy
        return set(spacy.util.get_installed_models())
    except Exception:  # noqa: BLE001
        return set()


def _sentence_transformer_local_path(short_name: str) -> str | None:
    """Return a local model path only if the model is already cached.

    The checked paths are intentionally conservative.  We never call a remote
    downloader; absence is reported as an unavailable candidate.
    """
    mapping = {
        ST_MPNET: ("sentence-transformers", "all-mpnet-base-v2"),
        ST_MINILM: ("sentence-transformers", "all-MiniLM-L6-v2"),
    }
    org_name = mapping.get(short_name)
    if not org_name:
        return None
    # Standard Hugging Face cache layout is either
    # ``HF_HOME/models--...`` (direct cache root) or ``HF_HOME/hub/models--...``.
    # Test both so a local cache mounted at ``HF_HOME`` or at the standard
    # ``hub`` subdirectory is found without any network access.
    cache_root = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface" / "hub")))
    candidate_roots = [cache_root]
    if cache_root.name != "hub":
        candidate_roots.append(cache_root / "hub")
    for root in candidate_roots:
        snapshots = root / f"models--{org_name[0]}--{org_name[1]}"
        if not snapshots.exists():
            continue
        for snapshot in sorted(snapshots.glob("snapshots/*")):
            if (snapshot / "config.json").exists():
                return str(snapshot)
    return None


def inventory_backends() -> list[dict[str, Any]]:
    """Return an inventory without downloading or mutating the environment."""
    rows: list[dict[str, Any]] = []
    installed = _spacy_installed_models()
    for short_name, env_name, mode in (
        (SPACY_MD, "en_core_web_md", "md_vector_cosine"),
        (SPACY_SM, "en_core_web_sm", "sm_text_similarity"),
    ):
        available = env_name in installed
        rows.append({
            "short_name": short_name,
            "kind": "spacy",
            "env_model": env_name,
            "mode": mode,
            "available": available,
            "download_required": not available,
        })
    for short_name, model_name in (
        (ST_MPNET, "sentence-transformers/all-mpnet-base-v2"),
        (ST_MINILM, "sentence-transformers/all-MiniLM-L6-v2"),
    ):
        package_available = False
        try:
            import importlib.util
            package_available = importlib.util.find_spec("sentence_transformers") is not None
        except Exception:  # noqa: BLE001
            package_available = False
        local_path = _sentence_transformer_local_path(short_name) if package_available else None
        rows.append({
            "short_name": short_name,
            "kind": "sentence_transformers",
            "model_name": model_name,
            "available": bool(package_available and local_path),
            "package_available": package_available,
            "local_snapshot": local_path,
            "download_required": not bool(package_available and local_path),
            "estimated_download_size_mb": 420 if short_name == ST_MPNET else 90,
        })
    return rows


def load_backend(short_name: str) -> SpacySimilarityBackend | SentenceTransformerBackend:
    if short_name == SPACY_MD:
        return SpacySimilarityBackend("en_core_web_md")
    if short_name == SPACY_SM:
        return SpacySimilarityBackend("en_core_web_sm")
    if short_name in (ST_MPNET, ST_MINILM):
        local_path = _sentence_transformer_local_path(short_name)
        if not local_path:
            raise BackendUnavailableError(
                f"{short_name} is not present in the local cache; download is forbidden in this task"
            )
        return SentenceTransformerBackend(short_name, local_path)
    raise BackendUnavailableError(f"unknown Stage 3-v2 semantic backend: {short_name!r}")


def _environment_versions() -> dict[str, Any]:
    import sys
    versions: dict[str, Any] = {"python": sys.version.split()[0]}
    try:
        import spacy
        versions["spacy"] = getattr(spacy, "__version__", None)
    except Exception:  # noqa: BLE001
        versions["spacy"] = None
    try:
        import numpy
        versions["numpy"] = getattr(numpy, "__version__", None)
    except Exception:  # noqa: BLE001
        versions["numpy"] = None
    return versions


def selected_backend_manifest(matcher: SharedSemanticMatcherV2,
                              *, gamma: float, theta: float,
                              calibration_grid: Mapping[str, Any],
                              calibration_objective: Mapping[str, Any],
                              development_family_ids: Sequence[str],
                              test_quarantine_statement: str) -> dict[str, Any]:
    """Build the deterministic freeze manifest for a selected backend."""
    return {
        "schema_version": "stage3_v2_semantic_backend_freeze@1.0.0",
        "status": "SEMANTIC_BACKEND_FROZEN",
        "selected_backend": matcher.identity(),
        "similarity_interface": "SharedSemanticMatcherV2.similarity(text_a, text_b) -> float",
        "similarity_policy": "cosine_or_spacy_text_similarity_as_identified; clamped to [0,1]",
        "normalization": {
            "unicode": "NFKC",
            "nbsp_replacement": True,
            "strip": True,
            "whitespace_collapse": True,
            "casefold": True,
        },
        "fine_tuning": False,
        "gold_used_for_selection": False,
        "cache_key_policy": "backend_identity_sha256 + normalized_text_a + normalized_text_b",
        "batch_order_independent": True,
        "pooling_policy": (
            "spacy_doc_vector_average (md) / spacy_doc_similarity tensor baseline (sm)"
        ),
        "cosine_policy": (
            "explicit normalized vector cosine clamped to [0,1] for md; preserved "
            "spaCy Doc.similarity clamped to [0,1] for sm"
        ),
        "library_versions": _environment_versions(),
        "model_identity": matcher.identity(),
        "gamma": float(gamma),
        "theta": float(theta),
        "calibration_grid": dict(calibration_grid),
        "calibration_objective": dict(calibration_objective),
        "development_family_ids": list(development_family_ids),
        "test_quarantine_statement": test_quarantine_statement,
        "llm_api_calls": 0,
        "network_calls": 0,
        "downloaded_models": [],
    }


__all__ = [
    "SCHEMA_VERSION",
    "SPACY_MD",
    "SPACY_SM",
    "ST_MPNET",
    "ST_MINILM",
    "CANDIDATE_SHORT_NAMES",
    "SemanticMatcherError",
    "BackendUnavailableError",
    "normalize_text_v2",
    "SpacySimilarityBackend",
    "SentenceTransformerBackend",
    "SharedSemanticMatcherV2",
    "inventory_backends",
    "load_backend",
    "selected_backend_manifest",
]
