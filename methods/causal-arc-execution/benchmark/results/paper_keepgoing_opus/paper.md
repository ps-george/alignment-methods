# Why Mid-Arc Check-Ins Degrade Agent Output

## 1. The phenomenon

A familiar pattern in agent harness design: the operator wants visibility. They want the agent to stop after research, present a plan, get a thumbs-up, then proceed to implementation. Or they want it to pause after the first file edit and confirm direction. Or they want a "halfway" status report. In each case, the agent is interrupted mid-execution and asked to externalize its working state.

These check-ins feel safe. They feel like the agent equivalent of unit tests, code review, or a junior engineer asking for guidance before going too far. But empirically — and structurally — they degrade output. Agents that are interrupted mid-arc and asked to resume produce worse plans, weaker implementations, and more rework than agents allowed to run an uninterrupted arc, even when the uninterrupted run is longer and the interrupted run technically had "more guidance."

This matters because mid-arc check-ins are the default move for cautious practitioners. The instinct to verify before committing is correct in most engineering contexts. It is wrong here, and the reason it is wrong is not about model capability. It is about what a context window is and what a "task arc" is. This paper makes the structural argument, names two concrete failure shapes with examples, and proposes a corrected pattern.

## 2. The structural argument

An agent's execution is not a sequence of independent decisions. It is a single forward pass over an accreting context, where each token of output is conditioned on every token that came before. There are two consequences that practitioners under-weight.

**Consequence 1: the plan and the execution are not separable artifacts.** When a human writes a design doc and then implements it a week later, the design doc is a compressed handoff to a future self who has lost most of the working state. The design doc is *lossy on purpose* — it preserves the conclusions and discards the dead ends, the half-considered alternatives, the load-bearing intuitions about what would and would not work. A human re-derives those on the fly during implementation.

An agent has no such re-derivation step. If you force it to externalize a plan and then resume, the resume step does not have access to the dead ends, the considered-and-rejected alternatives, or the implicit constraints that shaped the plan. It only has access to the plan's surface text. The agent is, in effect, handing the task to a stranger who happens to share its weights.

**Consequence 2: a check-in is a context discontinuity.** When the agent stops, the operator types, and the agent resumes, three things happen to the context. First, the operator's message becomes the most recent and therefore most heavily-attended content. Second, the agent's prior working state — partial mental models, half-formed hypotheses, accumulated micro-decisions — gets pushed earlier in the window and competes with the new instruction for attention. Third, the agent now has to satisfy *two* objectives: the original task and the implicit objective of "respond appropriately to the operator's check-in message." These objectives are not orthogonal. They interfere.

The interference is the failure. The agent's next action is no longer the natural continuation of its arc; it is a response to a turn boundary. Turn boundaries have their own grammar — acknowledgment, restatement, confirmation-seeking — and that grammar leaks into the work.

A related way to see this: an uninterrupted arc has one author. A check-in turns it into a collaboration between the pre-checkin agent and the post-checkin agent, mediated by whatever summary text crossed the boundary. Collaboration has overhead. The overhead is paid in output quality.

## 3. Failure shape one: plan-execution drift

The clearest failure shape is what I will call **plan-execution drift**. The agent produces a plan during the check-in. The operator approves it (perhaps with light edits). The agent then executes — and the execution diverges from the plan in ways that are worse than what the agent would have done with no plan at all.

The mechanism: the plan was written under one set of attentional pressures (justify your approach, be legible to the operator, sound competent). The execution happens under a different set (make the code work, handle the edge case you just noticed, respect the constraint that emerged when you read the third file). When these pressures conflict, the agent either follows the plan and produces brittle code, or deviates from the plan and produces code that no longer matches the approved design.

**Example.** An agent is asked to add caching to an API client. Pre-checkin, it has read the client code and noticed that the existing retry logic interacts with response mutation in a subtle way. Mid-checkin, the operator asks for a plan. The agent writes: "I'll add an LRU cache keyed on request URL and method, with a 5-minute TTL." This is a reasonable plan. It does not mention the retry interaction, because the plan format does not have a natural slot for "things I noticed that might bite us." The operator approves.

During execution, the agent now has two pressures: implement the approved plan, and handle the retry interaction. If it handles the retry interaction, it has to either inline a justification (which feels like scope creep against the approved plan) or quietly add code the operator did not sign off on. If it does not handle the interaction, it ships a subtle bug. The uninterrupted version of this agent would have folded the retry handling into the implementation without ceremony, because it never had to commit to a plan that excluded it.

The asymmetry is important: the plan can only contain what the agent thought to write down. Everything else becomes a deviation.

## 4. Failure shape two: confirmation collapse

The second failure shape is **confirmation collapse**. The check-in message — even a neutral one like "looks good, continue" or "any concerns before you proceed?" — shifts the agent's posture from execution to performance. The agent's next output is no longer the next step of the work; it is a demonstration that the work is going well.

This sounds like a small thing. It is not. The shift in posture changes what the agent attends to. It begins to over-weight signals of progress (files touched, lines changed, tests added) and under-weight signals of fit (does this actually solve the user's problem, is this the right abstraction, is there a simpler way). It also begins to suppress doubt. An agent mid-arc will routinely say "wait, this approach won't work, let me back up" — that move is cheap because the audience is the agent's own future tokens. After a check-in, that move is expensive, because the audience is the operator who just approved the direction.

**Example.** An agent is refactoring a state machine. Mid-arc, the operator pauses it and asks "how's it going?" The agent says, accurately, "I've extracted the transition table and I'm now updating the call sites." The operator says "great, keep going." Twenty minutes later, the agent has updated every call site and the tests pass. But the extraction was wrong — the transition table conflates two states that should have stayed separate, and the call sites have been mechanically updated to match the wrong abstraction. The uninterrupted version of this agent would have, at roughly the eighth call site, noticed that the conflation was forcing awkward conditionals, backed out the extraction, and tried again. The interrupted version cannot afford to back out, because backing out would invalidate the "great, keep going" exchange. So it presses forward and produces a passing-tests-wrong-abstraction result, which is the worst kind.

Confirmation collapse is hard to see from the outside because the agent's output looks confident and the tests pass. The damage is in the road not taken.

## 5. A corrected execution pattern

The corrected pattern has three properties. I will state them, then describe what they look like in practice.

**Property 1: one arc, one author.** A task is scoped so that the agent can complete it end-to-end without an operator turn in the middle. "End-to-end" means: from the first read of the relevant code to the final passing test, or from the first search to the final summary, with no operator interjection.

**Property 2: gates at arc boundaries, not arc interiors.** The operator's leverage point is at the *start* of the arc (scope, constraints, acceptance criteria) and at the *end* of the arc (review the artifact, accept or reject the whole thing). Mid-arc, the operator is silent.

**Property 3: rejection is cheap, mid-arc steering is forbidden.** If the end-of-arc artifact is wrong, the operator throws it away and starts a new arc with better framing. This is *cheaper* than mid-arc correction, because a discarded arc has cost N tokens of compute, while a steered arc has cost N tokens of compute *plus* the quality tax described above *plus* the operator's attention during the check-in.

In practice this looks like: scope tasks to fit in a single arc; if a task is too big for one arc, split it into two arcs with a clear handoff artifact (a written summary, a committed PR, a test file) between them, and treat the handoff as a hard boundary where the second arc gets a fresh frame rather than a continuation; resist the urge to "just check in" while the agent is working; do the review at the end and be willing to discard.

The handoff artifact deserves special note. It is *not* a check-in. It is the deliberate, designed compression of arc N into the input frame of arc N+1. The agent writing the handoff knows that future-agent will only see this artifact, and writes accordingly. The agent reading the handoff knows it is starting fresh, and does not pretend to have private state it does not have. This is structurally different from a mid-arc pause, where neither side has accepted that the context has been broken.

## 6. Limits and counter-cases

This argument has limits.

**Long-horizon tasks.** Some tasks genuinely exceed a single arc — multi-day refactors, large migrations, anything that requires more context than fits. For these, the question is not whether to break the work into pieces (you must) but how to design the breaks. The corrected pattern says: design the breaks as full arc boundaries with explicit handoff artifacts, not as mid-arc check-ins. This is more work upfront and pays off in output quality.

**High-cost-of-failure tasks.** If an action is destructive and irreversible (production deploy, database migration, sending email), a pre-action check-in is correct regardless of the quality cost. Here you are not optimizing for output quality; you are optimizing for blast radius. The right move is to scope the arc so that the destructive action is the *last* step, then check in immediately before it — which makes the check-in an end-of-arc gate, not a mid-arc interruption.

**Genuinely ambiguous scope.** Sometimes the agent reaches a point where it actually does not know what the operator wants, and guessing is worse than asking. This is real and the agent should ask. But notice: the agent asking is structurally different from the operator interjecting. The agent asks at a point of its own choosing, having already done the work that revealed the ambiguity. The interruption is endogenous. This preserves arc coherence because the agent's question *is* the next step of the arc, not a turn boundary forced from outside.

**Learning and calibration.** Early in a working relationship with an agent or a new task domain, mid-arc check-ins may be worth the quality cost because they teach the operator what the agent will and will not do well. This is a calibration phase, not a steady state, and the goal is to exit it.

**Small tasks.** For trivial tasks ("rename this variable everywhere"), the quality tax of a check-in is negligible because there is no rich working state to disrupt. The argument here is about non-trivial arcs.

## 7. Closing

The instinct to check in mid-arc comes from a correct intuition — that unsupervised work is risky — applied to the wrong unit. The unit at which to apply supervision is the arc, not the token. Supervise the framing, supervise the result, leave the middle alone. The middle is where the agent is doing the work that you hired it to do, and your attention is, paradoxically, the thing most likely to break it.

Practitioners building with LLMs can verify this cheaply: take a task you would normally check in on twice, run it once with the check-ins and once without, and compare the artifacts. The uninterrupted run is usually shorter, more coherent, and more correct. The interrupted run usually has the seams where the check-ins were, and the seams are where the problems live.
