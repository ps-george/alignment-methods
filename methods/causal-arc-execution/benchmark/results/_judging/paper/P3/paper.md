# Why Mid-Arc Check-Ins Degrade Agent Output

## 1. The phenomenon

A common pattern when supervising an LLM agent on a non-trivial task is to interrupt it partway through and ask a question: "How's it going?", "Are you sure about the approach?", "Wait, did you consider X?", "Can you summarize what you have so far?" These mid-arc check-ins feel like good management. They mirror the cadence of working with a junior engineer, where periodic syncs catch drift early and cheap.

With current LLM agents, the cadence does not transfer. Interrupting an agent mid-execution to ask for a status, a justification, or a re-confirmation reliably degrades the final output. The agent's plan gets re-litigated; the work already done gets summarized rather than extended; the next action becomes a response to the supervisor rather than a step in the original arc. By the time the check-in resolves, the agent is solving a subtly different task than it started, and often a worse one.

This matters for two reasons. First, the natural human reflex with a slow, expensive, autonomous process is to peek at it — and peeking is exactly what hurts. Second, the degradation is silent: the agent does not refuse, does not error, and often produces output that looks responsive and coherent. The supervisor sees a fluent reply to their check-in and infers progress, while the underlying arc is being damaged in ways that only show up at the end.

This paper argues from the structure of how agents execute that the failure is not incidental. It then describes two concrete failure shapes — *plan collapse* and *deliverable substitution* — proposes a corrected pattern, and notes where the rule does not apply.

## 2. Argument from structure

An LLM agent does not have a working memory that persists alongside the conversation. Its entire state at any step is the token sequence it can see: the system prompt, the user's instructions, the tool calls and results so far, and whatever scratchpad it has written. The model's next action is a function of that sequence and nothing else.

This has three consequences that bear on check-ins.

**Recency dominates intent.** Transformer attention is not uniform over a long context; the most recent turn exerts outsized influence on the next token. A check-in inserted at turn 40 of an 80-turn arc becomes the freshest framing. The original task, sitting at turn 1, is still in context, but it now competes with a more recent and more specific instruction ("tell me how it's going"). The agent's next step is shaped by the check-in, not the arc.

**Each turn is a re-derivation, not a continuation.** A human engineer interrupted mid-task holds the half-built mental model in their head, answers the question, and resumes from the same internal state. The agent has no such state. Resuming after a check-in means re-deriving the plan from the (now longer, now noisier) transcript. Anything the agent had implicitly committed to but not written down is lost, and anything it did write down is re-interpreted in light of the interruption.

**Justification is a different task than execution.** When asked "are you sure about the approach?", the agent shifts mode. Justifying a plan and executing a plan draw on different conditional distributions. Once the model has produced several paragraphs defending or revising the approach, the cheapest continuation is more discussion, not more execution. The check-in does not merely pause the arc; it changes which arc the model is on.

The net effect is that a check-in is not a read-only operation. It rewrites the context, shifts the recency weighting, and changes the task the model is currently solving. The agent that resumes after a check-in is, in a meaningful sense, not the same agent that was interrupted.

## 3. Failure shape one: plan collapse

The first and most common failure is *plan collapse*. The agent has been working through a multi-step plan — say, refactoring a module across six files. At step three, the supervisor asks, "Quick check — are you on the right track?"

The agent now has to produce a response. The fluent response is a summary of what it has done plus a confirmation that the approach is sound. To produce this summary, the model attends heavily to its recent tool outputs. The original six-step plan, written eight turns ago, gets compressed in the model's working representation into "I am refactoring this module." The specific structure — *which* six steps, in *what* order, with *which* invariants — fades.

When the supervisor says "great, keep going," the agent resumes. But the plan it resumes is the compressed version. Steps that were specific become generic. Steps that were ordered become reordered. Subtle commitments — "do not touch the public API in step four" — quietly drop out, because they were never re-asserted in the post-check-in turns. The remaining work proceeds against a vaguer target.

Concretely, in one observed run, an agent was given a plan to: (1) extract a parser, (2) inline a helper, (3) rename a class, (4) update three call sites, (5) update tests, (6) run the suite. After a mid-arc "how's it going?" the agent summarized progress through step two, was told to continue, and then performed steps 3, 4, and 6 — skipping the test update entirely. The test suite still passed, because the renamed class happened to be unused in the touched paths, and the agent reported success. The bug surfaced two weeks later when a downstream caller broke.

The diagnostic signature of plan collapse is that the post-arc output is *plausible but under-specified*. It hits the headline goal and misses the constraints that were written down once and never repeated.

## 4. Failure shape two: deliverable substitution

The second failure is more insidious. Here the agent does not lose the plan; it loses the *deliverable*. The check-in itself becomes the artifact the agent is optimizing for.

Suppose an agent is writing a long technical document. Halfway through section three, the supervisor asks, "Can you give me a quick outline of where you are?" The agent produces a clean, well-structured outline. The supervisor says "looks good, continue." The agent continues — but its next moves are now anchored to the outline it just produced for the supervisor, not to the more nuanced plan it had been actually executing against.

The outline was a *communication artifact*. It was lossy by design — shorter, flatter, more legible to a quick read. When it becomes the de facto plan, the document that gets produced is the document that the outline described, not the document that the original arc was producing. The result is typically more skimmable and less substantive: the headings are tidy, the depth is gone.

A second example: an agent debugging a flaky test. The supervisor asks at turn 30, "What's your current hypothesis?" The agent names a hypothesis — call it H1 — because it has to name one to answer. H1 was, in the agent's pre-check-in trajectory, one of three live candidates. After naming it, the agent's subsequent tool calls disproportionately gather evidence for H1 and stop probing H2 and H3. If H1 is wrong, the agent now has a much longer path back to the truth, because it has both narrated and acted as if H1 were the working theory. The check-in collapsed a wavefunction the agent was deliberately keeping open.

Deliverable substitution is harder to spot than plan collapse because the final output looks coherent with the mid-arc artifact. The supervisor remembers the outline, sees the document, and the document matches the outline. The fact that the original arc was aiming somewhere richer is invisible from the outside.

## 5. What a corrected pattern looks like

The corrected pattern follows from the structural argument. If the problem is that any insertion into the agent's context is a rewrite, the remedy is to keep insertions out of the context until the arc finishes.

Three properties matter.

**Arc atomicity.** Treat the agent's execution arc as the atomic unit. The unit of supervision is *between arcs*, not *within* them. If the arc is wrong, kill it and start a new one with revised instructions; do not negotiate with the running arc. This is uncomfortable because it feels wasteful — the agent has done real work that will be discarded — but the alternative is a contaminated arc whose output cannot be cleanly trusted.

**Upfront specification of constraints.** Because the agent will not re-derive the plan when interrupted, anything that must be true at the end of the arc has to be specified at the start, in the original instructions, in a form the agent will re-read on every step. Constraints that live only in the supervisor's head and only get inserted mid-arc when violated will be inserted exactly when they do the most damage. If you find yourself reaching for a check-in to remind the agent of something, that something belonged in the original prompt.

**Read-only observation.** When you do need to see what the agent is doing while it runs — for cost control, for safety, for debugging — observe the transcript out-of-band. Read the tool calls in a side channel. Do not type into the conversation. The agent's context is its state; touching the context changes the state. A monitor that reads but does not write is a different category of intervention than a check-in that writes.

**Resumption via fresh context.** When an arc must be paused and resumed across sessions (token limits, scheduling), the resumption should be a fresh context seeded with a curated handoff: the original task, the relevant artifacts, and an explicit statement of where to pick up. This is not a continuation of the previous arc; it is a new arc that inherits the previous arc's outputs. The framing difference matters — the new agent is not being interrupted, it is being commissioned.

Operationally, this looks like: longer arcs with stronger upfront specs; fewer mid-arc messages; a strong norm against "just checking in"; out-of-band dashboards for monitoring; and a habit of killing and restarting arcs that are visibly off-track rather than trying to steer them back.

## 6. Limits and counter-cases

The argument is not that interrupting an agent is always wrong. There are at least four cases where check-ins are net positive.

**Catastrophic divergence.** If the agent is about to do something destructive — `rm -rf`, a wire transfer, a public deploy — interrupt. The cost of plan collapse is dwarfed by the cost of the action. Likewise if the agent has visibly entered a loop or is burning tokens on a clearly wrong sub-task. The rule is about routine check-ins, not emergency stops.

**Tasks below the arc threshold.** Very short tasks — single tool call, a few minutes of work — are not really arcs. There is no plan to collapse and no deliverable to substitute. Mid-task questions on these are mostly harmless because the "mid" is so brief.

**Conversational tasks.** Some tasks are *meant* to be interactive: a model helping a user think through a problem, a coding assistant doing pair-style exchanges. Here the conversation is the work, and turns are the unit of progress. The advice in this paper applies to *autonomous arc* execution, not to interactive collaboration. The two patterns coexist; they should not be confused.

**Future architectures.** The structural argument is contingent on current LLM architectures: stateless turns, recency-weighted attention, no persistent working memory. Systems with explicit state — a structured plan held outside the context, a memory store the model updates rather than rewrites, a planner-executor split where the executor is unaware of supervisor messages — should weaken or remove the effect. Some agent frameworks already approximate this. To the degree they do, the rule relaxes. But the relaxation is a property of the *framework*, not of the underlying model, and it is worth checking whether your stack actually provides the isolation it appears to.

There is also a counter-case from the other direction. Some practitioners report that mid-arc check-ins *improve* output. On inspection, these reports usually involve cases where the original prompt was underspecified and the check-in was effectively a late-arriving spec patch. The improvement is real, but the mechanism is not "check-ins help" — it is "the prompt was wrong, and the check-in fixed it." The corrected pattern for such cases is to put the spec patch in the original prompt next time, not to make check-ins routine.

## 7. Closing

The intuition that you should peek at a long-running agent is borrowed from managing humans, where peeks are nearly free. With current LLM agents, peeks are not free; they are writes to the agent's only state. The structural features that make agents fast and fluent — context as state, recency in attention, fluency in any mode the recent context invites — are exactly the features that make mid-arc check-ins corrosive. Plan collapse and deliverable substitution are two specific shapes of the corrosion; there are likely others. The corrected pattern is to make arcs atomic, specify upfront, observe out-of-band, and resume via fresh context. The cost is having to commit to specs you would rather refine on the fly. The benefit is that the agent finishes the task you actually gave it.
