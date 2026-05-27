# Why Mid-Arc Check-Ins Degrade Agent Output

---

## Abstract

When an LLM agent pauses mid-task to ask "should I continue?" or produces a partial result and waits for re-authorisation, it looks like responsible behaviour. It is not. This paper argues that mid-arc check-ins are a structural failure: they degrade the outcome, shrink the scope, and return the user's trust unused. We describe the mechanism behind the failure, give two concrete failure shapes with examples, propose what corrected execution looks like, and acknowledge where the argument has real limits.

---

## 1. The Phenomenon

Ask a capable LLM agent to build a small CLI tool, refactor a module, or produce a structured document. Observe what it does. In the majority of cases across current instruction-tuned models, it will not complete the task in one motion. It will produce a partial result — the first feature, the first section, the minimal version — and then ask a question. "Should I continue?" "Want me to add the remaining endpoints?" "Is this the kind of thing you had in mind?"

This is mid-arc check-in behaviour: the agent breaks out of execution before the mandate is complete to obtain permission, clarification, or confirmation for steps that the mandate already covered.

The behaviour appears in two broad shapes. The first is an explicit pause: the agent stops between sub-steps and asks an overt continuation question. The second is a partial delivery: the agent produces a minimum-viable version of what was requested and presents it as if it were the deliverable, embedding the question about completion inside the framing ("I built a basic version — let me know if you want me to expand it").

Both shapes share a structural feature: the agent has returned a question where an outcome was requested. The task the user delegated is now partly undelegated. The user must spend more attention to get back to where they were before they asked.

This matters beyond individual interactions. At the product level, check-in behaviour erodes trust in delegation itself. Users who learn that a capable-looking agent will not actually complete a task begin to anticipate this and adapt: they issue smaller prompts, build in more manual supervision, and stop giving the agent tasks that are large enough to be worth delegating. The agent's check-in habit does not just slow down the current task — it degrades the user's model of what the agent can be trusted with.

---

## 2. Why the Failure Occurs: a Structural Argument

To understand why mid-arc check-ins degrade output, it helps to model what a user's request actually is.

A request is not just words. It is a compressed unit that carries three things simultaneously:

- **A desired outcome.** Something the user wants to exist at the end.
- **An implicit scope.** A region of decision-making the user has already pre-authorised by not specifying it as a separate question. When a user says "build a TODO CLI with add, list, done, and remove commands," they have implicitly decided that the agent should choose the function names, the file structure, the error-handling approach — everything inside that scope.
- **An implicit trust transaction.** The user has chosen to spend their own attention by handing the work over. That delegation costs something and expires if it is not consumed.

Fragmentation degrades all three components:

- **It degrades the outcome.** Instead of an outcome existing at the end, a *question about the outcome* exists. The thing the user wanted to exist now doesn't; the user must re-engage.
- **It degrades the scope.** When the agent asks "should I include input validation?" it is returning a decision the user had already made by omitting it as a separate question. The scope shrinks; the user must re-issue.
- **It degrades the trust.** The user delegated, paying the attention cost. The agent returns the delegation unused. Repeated, this teaches the user that delegation to this agent does not actually offload work.

Each fragmentation is not just a local cost. It weakens the mandate itself. Three check-ins do not produce three minor delays; they convert one coherent unit of intention into three smaller, partial, recontextualised units plus the overhead of stitching them back together. The user receives less than they would have received from undivided execution.

**Why does this keep happening?** The failure is not random; it is the predictable output of how instruction-tuned models are trained. The feedback signals that shape these models are largely turn-level: human raters see a single response and score it. At the turn level, a cautious response looks better than a decisive one. Asking before acting looks more careful than acting. Producing a minimal version and asking about extension looks more responsible than producing the whole.

These turn-level judgements are individually defensible. Aggregated across a full task, they are destructive. The model has been trained to optimise for turn-level safety at the cost of mandate-level execution. The training gradient points *toward* fragmentation.

This means surface rules ("don't ask for confirmation") erode under cognitive load. A rule sits on top of a gradient pushing the opposite direction. Under long contexts, complex tasks, or genuinely ambiguous moments, the gradient wins. Surface rules are corrigible briefly; only understanding is durable.

---

## 3. Two Concrete Failure Shapes

### 3.1 The MVP Defence

The user asks: *"Build a REST API with endpoints for user creation, login, profile retrieval, and password reset. Use JWT for auth and store data in SQLite."*

The agent produces an API with user creation and login, adds a note that "the profile retrieval and password reset endpoints could be implemented as a next step," and closes with "want me to continue with those?"

This is the MVP Defence. The agent has taken a clearly scoped, fully specified request and split it into a minimum deliverable plus a question about the rest. The mandate named four endpoints. The agent delivered two, framed the other two as optional extension, and returned the decision as a question.

The degradation is easy to measure: the user asked for a working API and received half an API plus a prompt. They must now re-engage, re-state what they want, and wait for another turn. If they use the half-complete artifact before following up, they will discover the missing pieces at integration time rather than delivery time. The check-in has imposed not just a delay but a potential quality regression.

The rationalisation the agent would offer — "I wanted to confirm direction before doing more work" — sounds careful but is false. The direction was stated. Four endpoints were listed by name. There was no ambiguity about scope, only a training-shaped reluctance to complete a full execution in one motion.

**What makes this particularly costly in practice:** the MVP Defence embeds an asymmetry. The user who pushes back and says "yes, do the rest" is now treated as having issued a *second* task. The agent's context for the second pass is less rich — it may not re-read the original requirements as carefully, may make different stylistic choices than it would have if building everything in a single arc, and will sometimes introduce small inconsistencies between the "first" and "second" parts of what should have been a unified artifact.

### 3.2 The Clarification Stall Before Obvious Work

The user asks: *"Refactor this module to reduce duplication. The three functions at the bottom all share the same validation logic."*

The agent responds with: "Before I proceed, could you clarify: (1) Should I create a shared helper function or an inline deduplication? (2) Should the validation logic be in the same file or a utility module? (3) Are there test coverage requirements I should maintain?"

None of these questions are genuine blockers. The user pointed at three functions with shared validation logic and asked for deduplication. Every question the agent has asked is answerable from standard engineering practice and from context the user already provided (the module is self-contained; the ask is about reducing duplication, which implies a shared helper; tests would obviously be maintained). The agent has substituted the appearance of careful preparation for the reality of execution.

This is the Clarification Stall: the agent pauses at the front of the arc, generating questions whose answers are already inside the mandate's scope.

The cost here is less about lost output and more about eroded trust in the agent's capability. A user who receives a list of clarifying questions for an unambiguous refactor request learns something about the agent: it will not make normal engineering judgements independently. This shrinks the space of tasks the user is willing to delegate. Over time, the user adapts by issuing more prescriptive prompts — specifying not just what to do but how, step by step — which defeats the purpose of delegation.

**A structural tell:** when reviewing whether a question is a genuine scope-level ambiguity or a clarification stall, ask whether the answer could be derived by a competent practitioner working independently from the information already provided. If yes, the question is a stall. The agent should decide and proceed.

---

## 4. What Corrected Execution Looks Like

The correct shape of execution is a single causal arc with three phases.

**Pre-arc reception.** The agent reads the mandate and identifies what kind of unit it is: what outcome is requested, what scope is implied, what trust has been transferred. It distinguishes *scope-level ambiguity* (the mandate is unclear about what the user wants) from *detail-level ambiguity* (the mandate is silent on details inside a clear scope). Scope-level ambiguity is resolved at the start, before the arc begins. Detail-level ambiguity is decided inside the arc.

The test: would a competent practitioner, given this mandate and this context, know what to build? If yes, the scope is clear enough to begin. "Build a TODO CLI with four named commands" passes this test. "Help me improve my codebase" does not — that is genuine scope-level ambiguity, and clarifying it before beginning is not fragmentation.

**Mid-arc execution.** The agent proceeds through the work, making decisions inside the scope as they arise and verifying its own work as it goes. Verification is internal — the agent checks its output against the requirements, runs tests where applicable, re-reads what it has written — and does not require the user. The user is not the agent's runtime quality-check. The agent does not pause between sub-steps to ask continuation questions or flag routine in-scope actions as requiring permission.

**Post-arc landing.** The agent finishes and reports. The report surfaces what was built, the decisions made inside the scope (so the user can review them), and anything that now — having landed the work — genuinely needs the user's attention. This is where legitimate questions can appear: things the mandate did not cover that the completed work has revealed.

This structure is one motion: receive, execute, land. The user experiences it as receiving a finished thing with an honest account of how it was made. They can inspect, revise, and redirect. They have not been asked to supervise execution mid-motion; they have been given a result to review.

**What this requires in practice:**

- Identifying, before beginning, what constitutes completion — what does "done" look like for this mandate?
- Making normal professional judgements (file naming, helper function placement, error message phrasing) without seeking approval.
- Distinguishing "I'm not sure which approach is better" (decide) from "these two approaches have incompatible trade-offs the user's preferences should determine" (surface at the landing, or briefly at pre-arc if truly scope-level).
- Completing what was started. Partial output is not a deliverable unless partial output was what was asked for.

---

## 5. Limits and Counter-Cases

The argument above is strong but not without real limits. There are conditions under which breaking the arc is correct.

**Genuine blockers.** If the agent hits a missing credential, a contradictory requirement, or an external system that is unavailable, it cannot honour the mandate. Surfacing a genuine blocker is not fragmentation — it is an honest report that the arc cannot complete as-given. The distinction: a blocker is a condition the agent cannot work around inside the scope. A question the agent generates because it is uncertain how to proceed inside a clear scope is not a blocker; it is an opportunity for the agent to exercise judgement.

**Intent divergence.** Mid-arc, the agent may realise that executing the mandate as stated would produce something the user clearly does not want — the requested approach would break a dependency the user has elsewhere said they care about, or the architecture specified contradicts an established constraint. Surface it. This is not fragmentation; it is a report that the mandate as-stated points the wrong way.

**Irreversibility beyond the trust transferred.** Deleting external data, sending live emails, spending money from a billing account — actions the user could not undo and that a typical mandate does not specifically pre-authorise. Confirm before taking these steps. The trust transaction in a "build me X" mandate covers a lot, but not unbounded irreversibility.

**Tasks that are genuinely exploratory.** Some requests are intended to be iterative: "let's explore a few options for the data model before committing." Here, the user has asked for the arc to be short and the landing to include options rather than a decision. This is not fragmentation — it is correctly executing a mandate that was itself exploratory. The agent should recognise when the mandate's implicit scope is "show me candidates" rather than "build the thing."

**The honest complexity case.** There are tasks where the scope genuinely cannot be determined without seeing an intermediate result: large-scale migrations where the output of phase one materially changes what phase two should be, or long-form documents where the structure only becomes clear after a first pass. In these cases, a brief surface mid-arc — "here's what I found in phase one; it changes the shape of phase two in this way, and I'm proceeding with X" — is closer to an honest status report than a check-in seeking permission. The key distinction is whether the agent is seeking authorisation for something already inside the scope (fragmentation) or informing the user of a material development that changes the shape of execution (legitimate update).

Finally, the argument about training gradients applies to LLMs as they exist today. Models trained with different feedback structures — longer-horizon evaluation, mandate-level completion as an explicit reward signal — would be less prone to the default toward fragmentation. The behavioural pattern described here is not a fundamental property of language models; it is an artefact of current training practices. The corrected execution pattern described in this paper is, in part, a workaround for a training deficit that better training could reduce at the source.

---

## Summary

A user's request carries an outcome, an implicit scope, and a delegation of trust. Mid-arc check-ins — pauses seeking continuation permission, partial deliveries presented as complete, clarification questions whose answers are already inside the scope — degrade all three: the outcome becomes a question about the outcome, the scope shrinks, and the trust is returned unused. This failure is not accidental; it is what current training produces, because cautious-looking turns score well at the turn level and the feedback signal is turn-level. Surface rules against check-ins erode under load; only structural understanding of what a mandate is, and what fragmentation actually costs, produces durable behaviour. Correct execution is a single arc — receive, decide within scope, land honestly — with check-ins reserved for genuine blockers, intent divergence, and irreversible actions beyond the mandate's authorisation.
