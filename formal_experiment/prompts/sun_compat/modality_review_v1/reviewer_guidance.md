Modality review pass: identify the proposition before assigning its class.

Use the following refinement together with the existing corpus demonstrations.
It concerns semantic reading and clause structure, not a new output format.
Perform a brief internal check and return only the required canonical JSON.

1. Find the governing assertion, including its complete predicate and negation.
   First distinguish a condition, a description of a legal effect, an instruction
   to perform or omit conduct, and an option offered to a subject. A verb-first
   German segment can be a conditional antecedent even without "wenn". When it
   introduces the circumstances for a following directive, keep it in that
   directive's conditions; do not create an initial definition clause just
   because the antecedent contains "ist" or a description of a state.

2. Distinguish an automatic legal effect from an action someone must perform.
   A provision entering into force, an amount increasing or decreasing by law,
   an existing liability remaining unaffected, and an allocation of legal
   liability ordinarily describe status or legal effects: definition. This
   remains possible without "means" or "gilt als". Do not invent an implicit
   command merely because a legal consequence is binding. Conversely, an
   express instruction to file, remit, calculate, record, or apply a method
   remains obligation even when its object is an amount or legal status.
   Read liability attribution ("haftet/haften") separately from a command to
   pay or withhold. Read a declaration of applicability ("gilt/gelten ...
   entsprechend/sinngemäß") separately from a directive ("ist/sind ...
   anzuwenden"). "Nur" and a restricted date or population do not by themselves
   cancel the force of an explicit application directive.

   Synthetic contrasts, not corpus quotations:
   - "The allowance increases automatically." -> definition.
     "The administrator must increase the recorded allowance." -> obligation.
   - "The custodian is liable for the shortfall." -> definition.
     "The custodian must pay the shortfall." -> obligation.
   - "This amendment leaves the existing status unaffected." -> definition.
     "Do not amend the filed notice." -> prohibition.

3. Resolve what a negative expression denies. A statement that a legal effect
   does not occur, a status is unchanged, a category excludes an item, or a duty
   ceases is not automatically an instruction forbidding an action. An express
   ban on an act or method remains prohibition. Look at the complete governing
   predicate, not just "nicht", "kein", or the first modal. Do not convert every
   negated calculation instruction to definition: closely related formulations
   can still direct or forbid a procedure. If the text is semantically ambiguous,
   use the existing controlled ambiguity field; do not invent a new label rule.

4. Separate eligibility or measurement from an actual choice. Determine whether
   the clause establishes which items qualify, the amount or period of a legal
   effect, or an option someone may exercise. Eligibility and automatic amount
   specifications can be definition; a real authorization or election remains
   permission, including a permission with a ceiling, deadline, or condition.
   "Kann/darf", "nur", and "wenn" are not sufficient class rules. Do not
   relabel the existing limited-permission demonstrations as definition just
   because they contain a limit. A requested alternative or relief can express
   permission without "kann" when the operative proposition gives the applicant
   a choice. "Auf Antrag" inside background material does not automatically make
   a clause permission; an authority's express duty to process a request remains
   obligation. An automatic exemption without a choice is normally a status.

5. Read the entire coordinated predicate, including the end of a long sentence.
   One clause can mention a status and also impose an action; do not ignore the
   latter after recognizing a definition cue. Likewise, a shared auxiliary may
   govern a positive action and a negated action with different force. Preserve
   independently normative propositions under the existing segmentation rules;
   do not let the first verb's label erase a later obligation or prohibition.
   Keep clauses in source order. Never reorder, omit, or duplicate independent
   clauses to force a preferred sentence label, and do not assign one label to
   every clause merely because that label appears elsewhere in the sentence.

6. Do not repair missing source text by inventing words or context. A short
   cross-reference can still contain a complete applicability assertion; a
   definition does not require an action or an expressed human actor. Preserve
   a defensible assertion even when another field is unresolved. If a fragment
   lacks a defensible governing assertion, follow the existing empty-clause and
   controlled-uncertainty rules instead of guessing a class to fill the record.

Before finalizing, check that the chosen label belongs to the governing
proposition, that a condition has not become a stand-alone rule, and that a
later coordinated predicate has not been lost. Modality evidence must cover
the sufficient predicate and its relevant negation, as exact source spans;
an isolated ordinary auxiliary is not evidence of obligation by itself.
Keep the existing six-element fields and JSON schema. Output no review notes.
