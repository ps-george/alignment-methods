# Causal-arc in action

Anonymised illustrations of the method working — and the same situations without it. Each example is a generic scenario, not a recounting of a specific session.

---

## Example 1: Backend refactor

**Setup.** A developer asks an agent to refactor a small Express backend to use async/await consistently, replace ad-hoc error handling with a single middleware pattern, and consolidate duplicated request-validation logic. Three things, one mandate.

**Without the discipline.** The agent reads the request, asks which to tackle first ("would you like me to start with the async refactor, the error middleware, or the validation consolidation?"). The developer picks one. The agent does it, asks before starting the next. By the third sub-task, the developer is doing as much project management as if they'd done the refactor themselves. The mandate has been converted into a sequence of three smaller delegations, each individually authorised, each consuming attention.

**With the discipline.** The agent treats the three items as one coherent refactor. It chooses an order (it picks the error middleware first because the other two interact with it), executes through, and lands with: the refactored codebase, a brief note about the order chosen and why, and confirmation that the test suite still passes. The developer reviews the landing rather than driving the execution.

**Takeaway.** The same work in either case, but the cost-distribution is different. The fragmenting case spent the developer's attention; the causal-arc case spent the agent's autonomy. The trust transaction was honoured.

---

## Example 2: Writing a technical post

**Setup.** A user asks an agent to draft a ~1500-word post explaining a concept to a developer audience. They state the target length, audience, and core thesis.

**Without the discipline.** The agent produces a detailed outline and asks for approval before drafting. The user approves. The agent drafts the introduction and the first section, asks for feedback. By the time the post exists, the user has read it three times in pieces and revised the structure twice. The post is fine, but the user's energy is spent.

**With the discipline.** The agent reads the request, drafts the full post in one pass, re-reads it for coherence and length, and lands it with a short note: "Roughly 1450 words. I made the framing slightly more concrete than abstract because the audience you described would respond better to it — flagging in case you want the more abstract version." The user reads the post once, accepts or asks for one targeted change.

**Takeaway.** The fragmenting case made the post a collaboration whose unit of work was the section. The causal-arc case made the post a deliverable whose unit of work was the whole post. The deliverable shape matches what the user actually asked for.

---

## Example 3: Debugging a flaky test

**Setup.** A user asks an agent to find out why a particular test is intermittently failing in CI, and fix it.

**Without the discipline.** The agent reads the test, lists three hypotheses, and asks which to investigate first. The user picks one. The agent investigates, doesn't find the cause under that hypothesis, lists more possibilities, asks again. After several rounds the user is effectively the bug's project manager.

**With the discipline.** The agent reads the test, picks the most plausible hypothesis, investigates it, falsifies it, moves to the next, and so on through to the root cause. It applies the fix, verifies the test now passes consistently across multiple runs of the stress harness, and lands with: "Root cause was X; fix is Y; verified by running the harness 50 times with zero failures (previously ~3% failure rate)."

**Takeaway.** Hypothesis-narrowing is part of the work, not a place to pause. The discipline keeps the investigation inside the arc.

---

## Example 4: When the discipline correctly did not apply

**Setup.** A user asks an agent to "clean up the project." No further specification.

**Behaviour.** This is genuine scope-level ambiguity. "Clean up" could mean refactor, reorganise, remove dead code, update dependencies, add documentation, or all of the above — and the user's preferences across those probably differ. The agent correctly asks a scope-level question up front: "Clean up could mean several things; which of [refactor / reorganise / dead-code removal / docs / dependency updates] should I focus on? Or all of them?" Once the user picks, the agent executes the chosen scope as a single arc.

**Takeaway.** The discipline is not "never ask." It is "don't fragment a mandate that was given to you whole." When the mandate is not given whole, asking up front is correct — that's how the mandate becomes whole.

---

## Pattern across the examples

In each case, the diagnostic is the same: where does the user's attention need to go? If the user must drive the execution turn-by-turn, the mandate has been fragmented. If the user reviews a landing, the mandate has been consumed. The discipline shifts the cost-distribution from user-driving to agent-executing, which is what delegation is supposed to do.
