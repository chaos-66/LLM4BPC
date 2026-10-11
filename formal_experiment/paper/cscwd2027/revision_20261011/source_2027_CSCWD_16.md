# 2027 原稿：按页、按栏提取的辅助阅读文本

> 来源为同目录 source_2027_CSCWD_16.pdf，六页，未经修订。
> SHA-256: f2ce8d2b020a41e71e56aca175b8568631e5ba1a1beb37a1b815d24641bf1948
> 这是机器提取文本，不是 LaTeX 源码。保留原稿中的错误供定位；数学上下标、公式、表格和图内文字可能失真，必须以原 PDF 为准。
> 每页先读左栏、再读右栏；跨栏页眉/标题单独列出。页末图注只作定位。
> 不要把这里的 Direct-LLM 等历史名称当成新的命名要求；修订时按阅读包的 LLM-SE 约定。

## PDF 第 1 页

### 跨栏标题与作者信息

Design-Time Business Process Compliance
    Checking with Large Language Models

          Yingchao Huo, Xiaoqing Chen, Jiahao Ma, Guosheng KangB, Wen Li, Jiayan Xiang
1Hunan Provincial Key Lab. for Services Computing and Novel Software Technology, HNUST, Xiangtan, Hunan, China
    2School of Computer Science and Engineering, Hunan University of Science and Technology, Xiangtan, China
 Email: {huoyingchao666, xiaoqingchen696, jiahaoma2627, guoshengkang, wenli0023cs, jiayanxiang02}@gmail.com

### 左栏

```text
Abstract—Design-time  business  process  compliance (BPC)
checking aims  to  identify potential  violations before process
execution. Existing approaches often rely on manually designed
linguistic rules and  syntactic patterns  to transform natural-
language  compliance  requirements  into  machine-processable
representations. This paper investigates large language model
(LLM)-based semantic extraction for design-time BPC check-
ing. Natural-language compliance requirements are transformed
into structured Rule Records containing modality, actor, action,
condition, constraint, and exception information. We compare
Direct-LLM with a reconstructed Rules-Only approach under
a common semantic representation and evaluation setting. We
further analyze the effects of prompt configurations and examine
how the resulting Rule Records influence downstream compliance
checking.
  Index  Terms—Business  Process  Compliance,  Design-Time
Compliance Checking, Large Language Models, Compliance
Requirement Parsing, Violation Detection

                           I. INTRODUCTION
  Business process compliance (BPC) aims to ensure that
business processes conform to applicable laws, regulations,
standards, and organizational policies [1]. Design-time BPC
checking identifies potential violations before process exe-
cution, but a major challenge is the semantic gap between
natural-language compliance requirements and formal process
models. Many existing approaches rely on compliance con-
straints that have already been formalized, making the trans-
formation of regulatory text into machine-processable repre-
sentations an important and often labor-intensive step [1, 2].
  To reduce this effort, Winter et al. [3] investigated com-
pliance assessment directly from regulatory documents. Sun
et al. [4] further proposed a design-time BPC framework that
extracts fine-grained regulatory semantics, including modality,
actor, action, condition, constraint, and exception, and matches
them with process-model information for violation detection.
Their semantic extraction combines syntactic analysis and
manually designed linguistic rules. While explicit and inter-
pretable, such extraction depends on predefined patterns and
linguistic resources.
  Recent work has explored Large Language Models (LLMs)
for legal requirement modeling, structured regulatory-rule ex-
traction, and BPC-related analysis [5–8]. Although some of
these studies adopt BPC-relevant semantics or extract fine-
grained regulatory information, their primary objectives differ
from directly comparing LLM-based and rule-based extrac-
tion of individual compliance requirements within a common
```

### 右栏

```text
design-time BPC setting.  It therefore remains useful to ex-
amine how Direct-LLM extraction behaves under the same
target representation and evaluation setting as a reconstructed
non-LLM baseline, and how the resulting Rule Records affect
downstream BPMN compliance checking.
  In this paper, we investigate Direct-LLM semantic extrac-
tion within this design-time BPC setting. Natural-language
compliance requirements are transformed into structured Rule
Records, while BPMN process models are converted into
structured process information for downstream matching and
violation analysis. We compare Direct-LLM with an inde-
pendent Rules-Only reconstruction under common inputs, se-
mantic representations, reference annotations, and evaluation
procedures. We further analyze the effects of different prompt
configurations and examine how the resulting Rule Records
influence downstream compliance checking.
  The main contributions of this work are:
  • We apply Direct-LLM extraction to an existing  fine-
     grained BPC semantic representation and generate struc-
     tured Rule Records for downstream compliance checking.
  • We conduct a controlled comparison between Rules-Only
    and Direct-LLM extraction, analyze their strengths and
     limitations at the semantic-element level, and examine
     the effects of different prompt configurations.
  • We connect the extracted Rule Records with downstream
    compliance checking and evaluate their effects on the
     three original violation types: missing action, incorrect
     actor, and out-of-order execution.
  The remainder of this paper is organized as follows. Sec-
tion II reviews related work. Section III presents the problem
formulation and framework. Section IV describes the method-
ology. Section V reports the experiments and  results, and
Section VI concludes the paper.

                        II. RELATED WORK

  Design-time business process compliance checking has been
studied using logic-based, pattern-based, and other formal
compliance representations [1, 2]. These approaches provide
precise and machine-processable constraints, but regulatory re-
quirements generally need to be formalized before automated
checking can be performed. To reduce this manual  effort,
Winter et al. [3] investigated compliance assessment directly
from regulatory documents. Sun et al. [4] further proposed a
design-time BPC approach that extracts fine-grained semantic
```

## PDF 第 2 页

### 左栏

```text
information from regulatory text and combines it with process-
model information for violation detection.
  Recent work has explored large language models (LLMs)
for legal and regulatory modeling. De Kinderen and Winter [5]
studied prompt-based generation of legal requirement models.
Barrientos et al. [6, 7] investigated regulatory-change detection
and its relevance or impact on business process compliance,
including BPC-relevant semantics related to the representation
of Sun et al. [4]. Guliani et al. [8] proposed De Jure, an LLM-
based pipeline for fine-grained structured extraction of regu-
latory rules with iterative evaluation and repair. These studies
demonstrate the potential of LLMs for regulatory analysis, but
their primary objectives differ from directly extracting individ-
ual compliance requirements under a shared Sun-style BPC
representation and comparing the resulting Rule Records in
the same design-time BPMN compliance-checking pipeline. In
contrast, this work conducts a controlled comparison between
a reconstructed non-LLM extractor and Direct-LLM under the
same target representation and evaluator, and further examines
their downstream compliance-checking outcomes.

      III. PROBLEM FORMULATION AND FRAMEWORK

A. Problem Formulation

  Following the design-time BPC setting of Sun et al. [4], we
consider a BPMN process model P and a natural-language
compliance requirement q. The process model is transformed
into a Process Record P, which contains process elements,
participants or actors, control-flow relations, and label seman-
tics. The compliance requirement is transformed into a Rule
Record R, which contains modality, actor, action, condition,
constraint, exception, and supporting evidence. Design-time
compliance checking then uses (P, R) for rule–process match-
ing and violation analysis.

B. Overall Framework

  As illustrated in Fig. 1, the proposed framework consists of
three stages: Process Model Parsing, Compliance Requirement
Parsing, and Compliance Checking. Stage 1 parses the BPMN
process model and organizes the extracted process elements,
participants, control-flow relations, and label semantics into a
structured Process Record. Independently, Stage 2 uses Direct-
LLM semantic extraction to transform the natural-language
compliance requirement into a structured Rule Record contain-
ing fine-grained compliance semantics. Stage 3 combines the
Process Record and Rule Record for rule–process matching
and detects missing-action, incorrect-actor, and out-of-order
violations. The detailed Direct-LLM procedure in Stage 2 is
presented in Section IV-B.

                   IV. METHODOLOGY

A. Process Model Parsing

  Following Sun et al. [4], Stage 1 uses a deterministic BPMN
parser to extract process elements, participant information,
```

### 右栏

```text
sequence flows, and textual labels. Sequence flows are fur-
ther used to derive control-flow edges, transitive reachabil-
ity, and activity-order relations. Actor, action, and business-
object semantics are obtained from process labels using a
fixed linguistic analysis procedure following the process-label
analysis strategy of Sun et al. The extracted information is
organized into a structured Process Record containing activ-
ities, participants, control-flow relations, and label semantics
for downstream compliance checking.

B. Compliance Requirement Parsing

  Stage 2 transforms each natural-language compliance re-
quirement into a structured Rule Record. Following the se-
mantic representation of Sun et al. [4], each record is orga-
nized into clauses containing modality, actor, action, condition,
constraint, and exception information. Span-bearing elements
are represented by source-anchored evidence spans with stable
identifiers and normalized values for downstream matching.
Character offsets use zero-based start and exclusive end posi-
tions, and the recorded evidence text must correspond exactly
to the associated source span. Actor–action associations ref-
erence the identifiers of extracted actors and actions, while
ordering relations reference the identifiers of their before/after
action endpoints.
  Prompt Design. As shown in Fig. 2, the prompt consists
of a shared base layer and three configurable components.
The shared base layer defines the extraction task, target Rule
Record schema, source and evidence representation, span and
identifier requirements, and the basic structural output inter-
face. It is retained throughout all prompt configurations. On
top of this base layer, E provides synthetic worked examples,
S provides detailed semantic interpretation guidance, and J
provides additional JSON and output-discipline instructions.
Only E, S, and J are varied in the factorial experiment, while
the shared base layer remains fixed.
  Direct-LLM Semantic Extraction. Given the requirement
and prompt, Direct-LLM directly generates structured seman-
tic elements, supporting evidence, and relations without using
predictions from the rule-based baseline or reference annota-
tions. The generated information is organized into a candidate
Rule Record under a unified JSON representation. This design
allows semantic extraction to be performed within a single
LLM  call while preserving the fine-grained representation
required by downstream compliance checking.
  Output  Validation and Normalization. The generated
candidate record is processed by a deterministic validation and
normalization procedure before being used in Stage 3. The
procedure checks schema conformance, exact correspondence
between evidence  text and source  offsets, containment of
element spans within their clauses, uniqueness of element
identifiers, and  referential consistency of actor–action and
ordering relations.  If an evidence span  is misaligned,  it  is
re-anchored only when the reported text has a unique exact
occurrence  in the corresponding source clause; otherwise,
the unrecoverable element  is removed. Normalized values
are retained for downstream semantic matching, while the
```

## PDF 第 3 页

### 左栏

```text
original evidence text and source offsets remain unchanged.
This procedure repairs structural and alignment errors without
introducing new semantic interpretations.

C. Compliance Checking

  Stage 3 combines the Process Record and Rule Record
for rule–process matching and violation detection. Following
Sun et al. [4], we retain the three original violation types:
missing action, incorrect actor, and out-of-order execution.
Let Ar and Ur denote the actions and actors contained in
rule r, respectively, and let sim(xr, xp) denote the semantic
similarity between a  rule-side element and a process-side
element. Thresholds τ, γ, and θ are used for rule–process
matching, action mapping, and actor comparison, respectively.
  Rule–Process Matching. Each rule action is matched to its
most similar process-side action, forming the candidate map-
ping set Dr,p. Rule actors are matched analogously, forming
Or,p. The action and actor matching ratios and the overall
rule–process matching score are defined as

               ∑︂    sim(ar, am) > τ
                     (ar,am)∈Dr,m
     mA(r, m, τ) =                                               ,
                               |Dr,m|
               ∑︂    sim(or, om) > τ       (1)
                      (or,om)∈Or,m
     mO(r, m, τ) =                                              ,
                               |Or,m|
       F(r, m, τ) = max{mA(r, m, τ), mO(r, m, τ)}.

When Ar =  ∅, mA(r, p; τ)  is defined as 0; analogously,
mU(r, p; τ) = 0 when Ur =  ∅. The resulting mappings
provide the basis for the three downstream violation checks.
  Missing-Action  Violation.  For  each  required  rule  ac-
tion ar ∈Ar,  let s(ar, p) = maxap∈Ap sim(ar, ap), with
```

### 右栏

```text
s(ar, p) = 0 when Ap = ∅. For |Ar| > 0, the missing-action
score is

      Br,m,γ = {(ar, am) ∈Dr,m | sim(ar, am) < γ}.   (2)


                                        |Br,m,γ|
          action violation(r, m, γ) =              .         (3)
                                        |Ar|

Thus, a rule action with no process-side candidate is counted
as missing. If Ar = ∅, the case is unevaluable for missing-
action checking and no decision is produced.
  Incorrect-Actor Violation. Actor checking  is performed
after  the corresponding  rule  action has been  successfully
mapped  to a process  activity. Let Rr,p,γ  denote the  rule
actors associated with successfully mapped actions and Cr,p,γ
the union of actor or business-object candidates bound to
those matched activities. Following the Sun-style definition,
for |Rr,p,γ| > 0 and Cr,p,γ ̸= ∅,

         Rr,m,γ = {︁ g ∈Pr | ∃(ar, am) ∈Dr,m,
                                                              (4)
                 fr(g) = ar ∧sim(ar, am) > γ }︁ .

         Cr,m,γ = {︁ r ∈bs obj(Am ∪Em) ∪Rm |
               ∃g ∈Rr,m,γ,                            (5)
                 sim(fr(g), fm(r)) > γ }︁ .

            Ir,m,γ,ϑ = {︁ r ∈Rr,m,γ | ∃r′ ∈Cr,m,γ,
                                                              (6)
                   sim(r, r′) < ϑ}︁ .

                                             |Ir,m,γ,ϑ|
         actor violation(r, m, γ, ϑ) =               .        (7)
                                         |Rr,m,γ|

For non-empty Cr,p,γ, this minimum test is equivalent to the
existential condition ∃up ∈Cr,p,γ  : sim(ur, up) < θ in Sun
```

### 图与图注（图形以原 PDF 为准）

Fig. 1: Overall framework for design-time business process compliance checking.

## PDF 第 4 页

### 左栏

```text
et al. [4]; the minimum form is used as an implementation-
equivalent rewriting. If the required actor, actor–action associ-
ation, or corresponding process-side candidate is unavailable,
the case is unevaluable for actor checking and no decision is
produced.
  Out-of-Order Violation. Ordering checks are performed
for rule-side ordering relations whose endpoints can both be
mapped to process  activities. Let Ur,p,γ denote the set of
evaluable ordering relations and Sr,p,γ ⊆Ur,p,γ the subset
satisfied by the process control flow. For |Ur,p,γ| > 0, the
out-of-order score is
      Ur,m,γ = {︁ (ur, u′r) ∈Ur |
           ∃{︁ (ur, um) ∈Dr,m, (u′r, u′m) ∈Dr,m }︁ ,    (8)
             sim(ur, um) > γ ∧sim(u′r, u′m) > γ }︁ .

      Sr,m,γ = {︁ (ur, u′r) ∈Ur,m,γ |
           ∃{︁ (ur, um) ∈Dr,m, (u′r, u′m) ∈Dr,m }︁ ,    (9)
            (um, u′m) ∈Fm ∧(u′m, um) /∈Fm }︁ .

                                 |Ur,m,γ| −|Sr,m,γ|
    order violation(r, m, γ) =                              .    (10)
                                      |Ur,m,γ|

An ordering relation is satisfied when the first mapped activity
can reach the second activity in the process control flow while
reverse reachability does not hold. If |Ur,p,γ| = 0, the case is
treated as unevaluable for out-of-order checking and no order-
violation decision is produced.

             V. EXPERIMENTS AND RESULTS

  We evaluate the proposed approach from three perspectives.
First, we compare Rules-Only and Direct-LLM  for  fine-
grained semantic extraction. Second, we analyze how different
prompt components affect Direct-LLM through a full factorial
experiment. Finally, we examine whether the extracted Rule
```

### 右栏

```text
Records lead to different downstream compliance-checking
performance.

A. Experimental Setup

  Stage  2  evaluation. We  use an  independently  recon-
structed EStG-150 benchmark containing 150 compliance re-
quirements. Its reference annotations form an LLM-assisted,
human-adjudicated Gold standard constructed for this study
rather than the original unpublished annotations of Sun et
al. [4]. Rules-Only and Direct-LLM are evaluated against the
same frozen Gold and evaluator. For actor, action, condition,
constraint, and exception, a prediction matches a Gold span
when  their character  intervals have a non-empty overlap;
Overall Micro-F1 pools TP, FP, and FN over these five fields.
Modality is evaluated separately by four-class Macro-F1 and
is excluded from the overall score.
  Rules-Only baseline. Rules-Only is an independent recon-
struction of the Stage 2 approach described by Sun et al. [4],
based on syntactic analysis and manually designed linguistic
rules. It is treated as a reconstructed baseline rather than the
original implementation. Both methods use the same frozen
inputs, Gold annotations, target representation, and evaluator.
  Direct-LLM and prompt configurations. All Direct-LLM
experiments use DeepSeek-V4-Pro-0813 with temperature 0,
top-p 1.0, and a maximum output length of 4096 tokens.
Table I and Table II are separate frozen runs; the provider
exposes no supported random seed, so  all differences are
interpreted descriptively without statistical-significance claims.
The shared prompt base remains fixed, while E, S, and J
denote semantic examples, semantic guidance, and additional
output discipline. Configuration 111 is the intact frozen full
prompt, the other configurations are controlled factorial vari-
ants, and 000 retains the shared base rather than representing
an unprompted LLM.
```

### 图与图注（图形以原 PDF 为准）

Fig. 2: Detailed workflow of Stage 2.

## PDF 第 5 页

### 左栏

```text
TABLE I: Semantic extraction performance of Rules-Only and
Direct-LLM.

          Element              Rules-Only   Direct-LLM

           Modality (Macro-F1)      0.713          0.769
           Actor                    0.820          0.758
           Action                   0.893          0.944
           Condition                 0.774          0.838
            Constraint                0.618          0.743
           Exception                0.880          0.762
           Overall (Micro-F1)∗       0.763          0.838
∗Pooled over actor, action, condition, constraint, and exception; modality is
                                excluded.


  Stage 3 evaluation. Stage 3 uses a separately constructed
GDPR-based benchmark because downstream checking re-
quires paired compliance requirements and BPMN models.
Nine GDPR rule texts are segmented into 74 sentences and
paired with 115 case records, yielding 201 applicable case–
type cells per method: 113 missing-action, 80 incorrect-actor,
and 8 out-of-order cells. These cells are fixed independently
of method outputs; an unevaluable prediction remains in the
evaluation, counting as FN for a violated reference and as
unknown rather than TN for a satisfied reference. Overall
precision,  recall, and F1  in Table  III pool  TP,  FP, and
FN over these cells. After development-stage calibration us-
ing a shared objective across both methods, Sentence-BERT
all-mpnet-base-v2 was selected with τ = 0.8, γ =
0.55, and θ = 0.45. Because the same benchmark was used
during development and calibration, the results are descriptive
rather than an independently held-out test.

B. Semantic Parsing Results

  Table I shows that the two approaches have different field-
level strengths. Direct-LLM achieves higher F1 for action,
condition, and  constraint, and  higher modality macro-F1,
whereas Rules-Only performs better for actor and exception.
The largest Direct-LLM gain occurs for constraint extraction,
increasing from 0.618 to 0.743. Overall pooled F1 over the five
span-bearing fields increases from 0.763 to 0.838, an absolute
improvement of approximately 7.5 percentage points.
  The results therefore do not indicate uniform superiority
across all semantic elements. Rules-Only remains stronger for
actor and exception extraction, while Direct-LLM performs
better on most of the remaining semantic fields. These field-
level results characterize the extraction behavior of the two
methods on EStG-150; the downstream experiment in Sec-
tion V-D is evaluated separately on the GDPR-based bench-
mark.

C. Prompt Factorial Analysis

  Table II shows a non-additive interaction among the prompt
components. Enabling E improves F1 in  all four matched
comparisons, making semantic examples the most consistently
beneficial component. In contrast, S provides substantial gains
when examples are absent but slightly decreases F1 when
```

### 右栏

```text
TABLE II: Factorial analysis of Direct-LLM prompt compo-
nents.

            E   S   J    F1   ∆F1 vs. 111

                0   0   0   0.7380      -0.0844
                0   0   1   0.7261      -0.0963
                0   1   0   0.8107      -0.0117
                0   1   1   0.8142      -0.0082
                1   0   0   0.8354     +0.0130
                1   0   1   0.8299      +0.0075
                1   1   0   0.8268      +0.0044
                1   1   1   0.8224      0.0000

TABLE III: Performance comparison of downstream compli-
ance checking.

        Method                Precision   Recall    F1

           Sun-style Rules-Only     0.3814     0.5362   0.4458
         Direct-LLM             0.4393     0.6812   0.5341


E is already present, suggesting partial overlap between ex-
amples and detailed semantic guidance. The effect of J  is
comparatively small and inconsistent. This does not imply that
structured output requirements are unnecessary, because the
shared schema and basic output constraints remain active in
every configuration.
  Configuration 100 achieves the highest observed F1 of
0.8354, whereas the intact full-prompt configuration 111 ob-
tains 0.8224. Thus, increasing prompt detail does not mono-
tonically improve extraction performance. Because the  full
prompt was frozen before the factorial experiment, configu-
ration 100 is treated as an ablation observation rather than a
post-hoc replacement of the main method.

D. Downstream Compliance Checking

  Rules-Only and Direct-LLM are applied to the same GDPR
compliance texts, and their resulting Rule Records are pro-
cessed by the same frozen Stage 3 pipeline. Table III reports
pooled performance over the 201 applicable evaluation cells.
Direct-LLM achieves an overall F1 of 0.5341 compared with
0.4458 for Rules-Only, an absolute gain of 8.83 percentage
points. Recall increases from 0.5362 to 0.6812 and precision
from 0.3814 to 0.4393. At the violation-type level, missing-
action F1 increases from 0.4554 to 0.4935 and incorrect-actor
F1 from 0.4262 to 0.5684, while both methods obtain 0.5000
for out-of-order checking.
  These downstream scores should not be directly compared
with the Stage 2 extraction scores because the two experi-
ments use different benchmarks, tasks, and evaluation units.
Downstream checking additionally requires the extracted com-
pliance semantics to be aligned with BPMN activity labels
and process-control information. A post-hoc analysis of the
frozen missing-action results identifies 50 of 70 false-positive
method–case cells (71.4%) as mapping-related and 20 (28.6%)
as broadly scope-related. Only 11 of the  latter satisfy the
stricter criterion for safely removable scope errors. Since this
analysis concerns missing-action false positives only, it should
not be interpreted as a decomposition of all Stage 3 errors. The
```

## PDF 第 6 页

### 左栏

```text
results nevertheless identify rule–process semantic alignment
as a major remaining limitation.

                   VI. CONCLUSION

  This paper  investigates Direct-LLM semantic  extraction
within a three-stage design-time BPC framework. Rules-Only
and Direct-LLM produce the same structured Rule Record
representation, enabling controlled comparison in Stage 2 and
downstream evaluation under the same Stage 3 pipeline. On
EStG-150, Direct-LLM performs better for modality, action,
condition, and constraint, while Rules-Only remains stronger
for actor and exception; Overall Micro-F1 over the five span-
bearing fields increases from 0.763 to 0.838. The factorial
analysis further shows that semantic examples provide the
most consistent prompt benefit, while detailed semantic guid-
ance and  additional output  discipline  exhibit non-additive
effects.
  On  the  separate GDPR-based development benchmark,
Direct-LLM Rule Records yield a downstream F1 of 0.5341
compared with 0.4458 for Rules-Only under the same check-
ing pipeline. These results should not be interpreted as a direct
field-level transfer of the EStG-150 results. The downstream
analysis identifies rule–process semantic alignment, particu-
larly the alignment between extracted compliance actions and
BPMN activity labels, as an important remaining challenge.
Future work will therefore focus on improving this alignment
and evaluating the approach on independently held-out bench-
marks.

             ACKNOWLEDGMENT

  This work  is  partially supported by the Hunan Provin-
cial Natural Science Foundation of China under Grant No:
2026JJ50519. Guosheng Kang is the corresponding author.

                 REFERENCES

[1] M. Hashmi, G. Governatori, H.-P. Lam, and M. T. Wynn,
    “Are we done with business process compliance: state of
    the art and challenges ahead,” Knowledge and Information
    Systems, vol. 57, no. 1, pp. 79–133, 2018.
[2] A. Zasada, M. Hashmi, M. Fellmann, and D. Knuplesch,
    “Evaluation of compliance rule languages for modelling
    regulatory compliance requirements,” Software,  vol.  2,
    no. 1, pp. 71–120, 2023.
[3] K. Winter, H. van der Aa, S. Rinderle-Ma, and M. Wei-
    dlich, “Assessing the compliance of business process mod-
    els with regulatory documents,” in Conceptual Modeling.
    Springer, 2020, pp. 189–203.
[4] X. Sun, S. Yang, C. Zhao, and D. Yu, “Design-time
    business process compliance assessment based on multi-
    granularity semantic information,” The Journal of Super-
    computing, vol. 80, no. 4, pp. 4943–4971, 2024.
[5] S. de Kinderen and K. Winter, “Towards taming large
    language models with prompt templates for legal grl mod-
    eling,” in Enterprise, Business-Process and Information
    Systems Modeling.  Springer, 2024, pp. 213–228.
```

### 右栏

```text
[6] M. Barrientos, K. Winter, and S. Rinderle-Ma, “Impact
    analysis of regulatory requirement changes on business
    process compliance,” Information and Software Technol-
    ogy, vol. 194, p. 108079, 2026.
[7] M. Barrientos, J. Loebbecke, K. Winter, and S. Rinderle-
   Ma, “Taming the complexity of legal change for business
    process compliance,” Business & Information Systems
    Engineering, pp. 1–26, 2026.
[8] K. Guliani, D. Gill, D. Landsman, N. Eshraghi, K. Kumar,
   and L. Gondara, “De jure: Iterative llm self-refinement for
    structured extraction of regulatory rules,” arXiv preprint
    arXiv:2604.02276, 2026.
```
