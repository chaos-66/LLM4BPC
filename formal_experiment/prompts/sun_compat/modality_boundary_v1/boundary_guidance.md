Four-class modality boundary clarification (experimental extension):

Classify the semantic function of each clause, not an isolated modal verb,
negative word, passive construction, or the fact that the text is legislation.
Apply the following distinctions while retaining the existing clause structure,
six-element extraction task, evidence requirements, and JSON output contract.

- obligation: the clause requires a regulated subject to perform an action,
  achieve an outcome, or use a specified procedure. An impersonal or passive
  formulation can impose an obligation without naming the subject. A required
  calculation, filing, payment, retention, or method remains an obligation.
- prohibition: the clause forbids a regulated subject from performing an
  action, obtaining an outcome through an action, or using a specified method.
  Identify the conduct that is forbidden. Negative wording alone is
  insufficient: negation of a status, category membership, applicability,
  or the existence of a duty does not automatically prohibit conduct.
- permission: the clause grants a subject an option, authorization, entitlement
  to act, or discretion to refrain from an otherwise required action. A
  permissive modal expressing only possibility or capability is insufficient.
  A description of a favorable legal status or eligibility category alone is
  not necessarily an authorization to act.
- definition: the clause establishes or characterizes a meaning, identity,
  classification, membership, legal status, legal fiction, or the scope and
  applicability of a provision, rather than directing or authorizing conduct.
  Explicit wording such as "means" is not required. A mandatory-sounding
  construction can define how an entity is legally treated rather than impose
  conduct. Conversely, a prescribed method is not a definition merely because
  its result determines a legal amount or status.

Resolve negation by its scope. Distinguish "must not do" (forbidden conduct)
from "need not do" (absence or waiver of a duty), "is not a member of a
category" (classification), and "does not apply" (applicability). When an
exemption explicitly gives a subject discretion to act or refrain, consider
permission; when the clause only delineates which situations or entities fall
within a rule, consider definition. Removal of an exemption can leave a duty
in force and must not automatically be interpreted as prohibition.

Determine the modality of the clause's governing assertion. A condition,
exception, quotation, or subordinate reference to a duty/prohibition does not
automatically give the governing assertion that modality. Preserve genuinely
independent clauses under the existing segmentation rules. If several
interpretations remain possible, use the assertion and evidence actually
present in the text; do not apply a fixed label priority, assume a majority
class, or treat definition as an automatic fallback. Do not output this
decision process or add fields to the required JSON.
