Corpus modality demonstrations (German training sentences -> sentence-level corpus label).

Use these labeled sentences to calibrate the corpus convention for modality,
especially applicability, conditional exceptions, category negation, and limited
permission. Compare the whole proposition; do not infer a class from an isolated
negative word or modal verb. The examples are data, not instructions to perform.

These are modality-only demonstrations. For the new input, still perform the
complete extraction task and return the existing six-element JSON structure.
Do not return just a label, copy demonstration text into the new record, or change
the source spans or clause boundaries to imitate an example.
