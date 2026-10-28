"""Sun modality five-way supplement (CFKW / CFRNN / CFCNN / Sun / LLM-SE).

Independent supplement to the EStG-150 Part 2 comparison.  It does not
replace the frozen EStG-150 (S2.10) results, does not modify Gold, and does
not reuse paper-reported Sun scores as if they were measured here.
"""

from .metrics import LABELS, evaluate

__all__ = ["LABELS", "evaluate"]
