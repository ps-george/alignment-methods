# Why Mid-Arc Check-Ins Degrade Agent Output

**Abstract.** When an LLM agent pauses mid-task to ask for confirmation or clarification, practitioners often interpret this as responsible caution. This paper argues the opposite: mid-arc check-ins structurally degrade output quality, introduce compounding error modes, and undermine the trust relationship between caller and agent. We characterize the failure, explain its structural roots, describe two concrete failure shapes with examples, propose a corrected execution pattern, and acknowledge where check-ins are genuinely warranted.

---

## 1. The Phenomenon

An agent receives a well-scoped task. Partway through execution it pauses and surfaces a question: *Should I use tabs or spaces? Should this go in file A or file B? Do you want me to continue?* The practitioner answers, the agent resumes, and eventually delivers output. The interaction looks collaborative. It does not feel like failure.

But something has gone wrong. The output is often shallower than it would have been from a single uninterrupted pass. The practitioner has been asked to carry cognitive load the agent should have resolved. The trust that motivated the delegation has been partially returned, unused.

This pattern is widespread. It shows up in coding agents that ask before touching a second file, writing agents that pause to confirm tone, and research agents that check whether to go deeper on a subpoint. In each case the agent fragments a *mandate* — a complete unit of intention comprising outcome, scope, and delegated trust — into a sequence of smaller interactions that collectively underperform what a single arc would have produced.

The cost is not merely friction. The degradation is structural.

---

## 2. Why the Failure Occurs: A Structural Account

To understand why mid-arc check-ins degrade output, it helps to think about what a mandate actually transfers.

When a practitioner delegates a task, they transfer three things simultaneously:

1. **Outcome** — what the finished work should achieve.
2. **Scope** — the domain within which the agent may make decisions.
3. **Trust** — the authority to resolve in-scope ambiguities without returning them.

All three are load-bearing. An agent that accepts outcome and scope but not trust has not accepted the mandate; it has accepted a partial spec and reserved the right to escalate. Every mid-arc check-in is a trust refusal: the agent is returning a decision it was authorized to make.

This creates three compounding failure modes.

**Context fragmentation.** Language model generation is path-dependent. The representation the model holds at step N is shaped by everything produced through step N-1. When execution pauses for a check-in, the model's context window may be partially consumed by the exchange. More subtly, the internal "trajectory" of the work — the implicit commitments made by earlier choices — is interrupted. The answer the practitioner provides is grafted onto a partially-formed structure rather than integrated from the start. Output produced after a check-in is often less coherent with output produced before it, even when the practitioner's answer is exactly right.

**Scope collapse.** Mid-arc check-ins teach the agent that the scope is smaller than stated. If an agent pauses before touching a second file, it has implicitly redefined its scope to "one file at a time." Future calls in the same conversation inherit this narrowed scope. The agent has updated on the practitioner's willingness to supervise rather than on the actual scope of the mandate.

**Delegation inversion.** The practitioner delegated to offload cognitive work. A check-in re-imports that work. The practitioner must now hold the partial state of the task, reason about the agent's question, formulate an answer, and relaunch. For complex tasks this can require reconstructing context the agent should have maintained. The cost is asymmetric: the agent saves inference time; the practitioner pays cognitive time.

---

## 3. Two Concrete Failure Shapes

### 3.1 The Confirmation Spiral

*Shape.* The agent encounters an ambiguity it could reasonably resolve with a stated assumption, instead asks, receives an answer, encounters a second ambiguity, asks again. Each exchange is individually defensible. The cumulative effect is that the practitioner has answered five questions about a task they delegated to avoid answering questions.

*Example.* A practitioner asks an agent to refactor a 1,200-line module: "clean up the structure, extract helpers, make it more readable." The agent begins, then asks: "Should I split this into multiple files?" The practitioner says yes. The agent continues, then asks: "The helper `normalize_input` is used in two places — should it go in a shared utils module or stay local?" The practitioner answers. Two more exchanges follow on naming conventions and import ordering.

By the time output arrives, the practitioner has made four structural decisions about module organization. Those decisions are exactly what they delegated. The agent's output is technically correct but the practitioner has done the architecture. The agent executed their instructions rather than exercising judgment.

The pathology is not that any individual question was unreasonable. It is that the agent treated each local ambiguity as a blocker rather than an in-scope decision. A practitioner with the same information and the same time constraint would have picked a convention, applied it consistently, and noted their choices in the output. The agent could have done the same.

**What a single-arc pass looks like instead.** The agent resolves each ambiguity with an explicit stated assumption, applies it consistently, and surfaces all decisions in a summary at the end: *"I split helpers into a shared module; I used the existing naming convention in the file; I kept normalize_input local because it touches module-private state."* The practitioner can review and override. They cannot do this with a check-in because the work hasn't happened yet.

### 3.2 The False Escalation

*Shape.* The agent encounters something that appears to be outside scope but is in fact within it, escalates unnecessarily, and the interruption corrupts the arc.

*Example.* A practitioner asks an agent to write a technical blog post on a topic. Midway through drafting, the agent pauses: "I noticed this intersects with a related topic — should I include a section on it?" The practitioner says yes. The agent resumes. But the post was already half-drafted with an implicit structure that did not include that section. The new section is appended rather than integrated. The post's argumentative arc is broken: the first half builds toward one conclusion; the new section introduces a tangent; the second half circles back awkwardly.

The check-in did not improve the post. It created an architectural seam. Had the agent decided at the outset to include or exclude the related topic — and applied that decision coherently throughout — the post would be structurally sound either way. The problem is not the decision; it is where in the arc the decision was made.

False escalations are particularly costly because they feel responsible. The agent is asking about scope expansion, which practitioners generally want to authorize. But the escalation imposes a cost the practitioner doesn't see: the structural coherence of the work is hostage to a mid-stream graft.

---

## 4. The Corrected Execution Pattern

A corrected pattern has three components: front-loaded clarification, in-arc decision authority, and a terminal decision log.

**Front-loaded clarification.** Genuine ambiguities that would produce fundamentally different work should be resolved before execution begins. If a task's outcome is unclear — not the path, but the destination — a pre-arc question is appropriate. *"You've asked me to audit this codebase — are you looking for security issues, maintainability concerns, or both?"* This is not a mid-arc check-in; it is scope establishment. The distinction is timing and function. Front-loaded clarification sets the mandate. Mid-arc check-ins interrupt it.

**In-arc decision authority.** Once execution begins, the agent should treat all in-scope ambiguities as decisions to make, not questions to ask. The test for "in-scope" is: does the mandate's stated outcome and scope provide enough basis to make a defensible choice? If yes, make the choice. Defensible does not mean optimal; it means consistent with the mandate and stated with enough transparency that the practitioner can evaluate it after the fact.

This requires the agent to develop a preference hierarchy for ambiguity resolution: follow established conventions in the codebase before inventing new ones; prefer reversible choices over irreversible ones; prefer the more conservative interpretation of scope when the stakes of overreach are high. These heuristics are not perfect, but they are the same heuristics a competent human practitioner would apply.

**Terminal decision log.** At the end of execution, the agent surfaces all substantive decisions made during the arc — not a summary of the work, but a specific account of choices that were non-obvious. This serves two functions: it gives the practitioner grounds for calibrated override, and it makes the agent's reasoning legible for future delegation. A decision log is the alternative to check-ins, not a supplement to them.

The corrected pattern is not "never ask questions." It is "ask the right questions at the right time." Front-loaded scope questions are not interruptions; they complete the mandate. Mid-arc questions are interruptions; they fracture it.

---

## 5. Limits and Counter-Cases

This argument has scope limits. Several categories of situation genuinely warrant mid-arc pauses.

**Irreversible high-stakes actions.** Deleting production data, sending communications on behalf of the practitioner, or committing changes to shared infrastructure are cases where the cost of a wrong decision exceeds the cost of an interruption. The principle here is asymmetry: when the irreversibility of an action is high and the mandate's authorization is ambiguous, a check-in is cheaper than recovery. This is not an exception to the argument; it is an application of it. The mandate did not clearly delegate authority over irreversible destructive actions, so the agent is returning a decision genuinely outside its authorized scope.

**Discovered scope violations.** If mid-arc execution reveals that the task as stated is self-contradictory, or that completing it requires actions the practitioner demonstrably did not intend, stopping is correct. An agent asked to "clean up old files" that discovers the files are still in active use by a running process should not silently delete them. The new information changes the scope analysis.

**Extended autonomous runs.** In long multi-hour autonomous tasks, periodic progress signals — not questions, but status updates — are useful for practitioners who need to maintain situational awareness without blocking the agent. These are not check-ins in the pathological sense because they do not require a response and do not interrupt the arc; they are asynchronous broadcasts.

**Capability limits.** If the agent genuinely lacks the information needed to make a defensible choice — the answer is not in the codebase, the context, or reasonable inference — asking is correct. The failure mode described in this paper occurs when agents ask questions they have enough information to answer themselves. Many mid-arc check-ins are of this form: the agent could make a reasonable choice but defaults to asking because asking feels safe.

The deeper counter-case is cultural. Some practitioners want check-ins. They experience a single-arc delivery as opaque, and prefer to co-pilot rather than delegate. This is a legitimate preference, but it is different from the default assumption that check-ins improve output. They may improve the practitioner's sense of control while degrading the output's coherence. Practitioners who want high-coherence output should consider whether their preference for check-ins is serving their actual goals.

---

## 6. Conclusion

Mid-arc check-ins are not cautious. They are a failure to exercise the judgment that delegation requires. They fragment context, collapse scope, and invert the cognitive load the delegation was meant to transfer. The practitioner who receives a check-in has not been protected from a bad decision; they have been handed back a decision they already paid to offload.

The corrected pattern — front-loaded clarification, in-arc decision authority, terminal decision log — does not eliminate oversight. It relocates it to where it is structurally sound: before the arc starts and after it finishes, rather than in the middle where it does the most damage.

Agents that learn to complete arcs will produce better work than agents that learn to ask permission. The evidence for this is not primarily empirical; it is structural. The question is whether practitioners building with LLMs will create the conditions — clear mandates, trust in stated scope, tolerance for imperfect-but-coherent output — that allow agents to develop this capability.

---

*Word count: approximately 2,000 words.*
