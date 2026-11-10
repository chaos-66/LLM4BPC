Integrated modality guidance (sentence candidate v1)

Read the entire input before assigning modality. Produce the clause-level
Rule Record and the sentence-level modality as two distinct outputs.

For each proposition, locate its complete predicate, grammatical subject,
negation, and scope. Identify whether the surrounding text supplies a
condition, an exception, introductory framing, a reported proposition,
or an independently asserted rule.

A German verb-first segment may introduce a condition. Attach that condition
to the following assertion when its syntax and meaning require this.
Framing such as "gilt Folgendes" requires inspection of the following content.
A complete assertion such as "die Vorschrift gilt entsprechend" can itself
state applicability. Decide from the complete construction.

Inspect every coordinated predicate, including predicates near the end of
the sentence. A shared auxiliary can govern several actions with different
polarity or normative force. Represent those differences in the relevant
clause labels. Check that every extracted action agrees with the modality
of the proposition to which it belongs. Keep independent clauses in source
order; never reorder, omit, or duplicate them to force a sentence label.

Use these distinctions together with the verified corpus demonstrations:

- Definition describes meaning, classification, legal status, applicability,
  eligibility, or a calculation relationship.
- Obligation requires conduct, an outcome, or the execution of a procedure.
  Passive and impersonal constructions can express an obligation.
- Prohibition excludes conduct or a method through a normative restriction.
- Permission grants an option, authorization, or discretion to a subject.
  Conditions, limits, and deadlines can qualify a genuine permission.

Determine what the predicate says about its subject. An amount changing
automatically and an instruction to change a recorded amount require
different readings. Legal recognition of a status and an instruction to
perform an assessment also require separate readings. A reference to
calculation, taxation, or an amount does not determine the class by itself.

Resolve negation locally. Check whether it concerns an action, a category,
applicability, a legal effect, or the existence of a duty. Interpret modal
verbs together with their complete predicates. Preserve explicit procedural
instructions even when the surrounding sentence defines a scope or amount.
Neither negated calculation nor conditional wording determines a class.
A negative word alone does not establish prohibition. Similar negative
expressions can have different corpus labels; do not invent a lexical rule
to remove an unresolved boundary.

For eligibility and permission, identify the proposition being asserted.
Does it delimit which objects or circumstances qualify, or grant a subject
a choice? Consult both supporting and contrasting demonstrations. A numerical
ceiling, a condition, or "nur" alone cannot settle this distinction. Preserve
the permission reading when an actual choice is qualified by a limit.
An applicant's choice and an authority's duty to process a request are
different propositions; a background mention of an application is not itself
a permission. Possibility or capability alone is not an authorization.

After reading all propositions, determine the sentence-level label from the
governing assertion and the demonstrated sentence-label convention.
Introductory framing and dependent conditions inherit their role from the
assertion they qualify. When several independent propositions have different
modalities, use the best-supported full-sentence interpretation and record
mixed_independent_modalities. Their order alone does not determine the label.
Do not impose a universal priority among the four classes, assume a majority
class, or use definition as an automatic fallback.

Support the selected sentence label with short, exact excerpts containing
the relevant predicate and negation. Separate excerpts may cover a
discontinuous predicate. Keep each independent proposition's own modality
in the Rule Record. Never copy the sentence label to all clauses.

If the visible text contains a defensible assertion despite a missing detail,
classify that assertion and record the uncertainty where needed. If the
fragment lacks a defensible governing assertion, return a null sentence
label with incomplete_input. Do not reconstruct absent legal text.
When the corpus boundary remains ambiguous, give the best-supported label
and record corpus_boundary_ambiguous. These flags express uncertainty, not
an alternative label or a reason to remove a sample from evaluation.

Return only the versioned JSON required by the supplied output schema.
