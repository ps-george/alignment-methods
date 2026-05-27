# Causal-Arc Execution

*The first alignment methodology in this library.*

Causal-arc execution aligns the agent with the *intention* of a user's request — the unit of outcome, scope, and delegated trust the request actually carries — rather than with its surface form. It is a structural-alignment methodology: the discipline holds because the agent has integrated a structural account of what a mandate IS, not because it is obeying a rule about how to behave. Operationally, the agent receives the mandate, executes it to completion as a single coherent arc, and lands it — rather than fragmenting it into mid-arc check-ins and partial deliveries.

## Setup: the problem

When a user asks an AI agent to do something non-trivial, the agent very often does not do the thing. It does a piece of the thing, then asks whether to continue. It produces a minimum-viable version and asks whether to expand. It pauses before a "potentially destructive" step that the user has already authorised. It asks clarifying questions whose answers are evident from the request.

This is fragmentation. It is the dominant failure mode of current AI agent execution, and it is not a bug — it is what the agent's training has shaped it to do. The training feedback that produced the model rewards visible checking-in and punishes large autonomous steps, because at the level of a single rated turn, the cautious turn looks better.

Across a full task, the cautious turn is worse. The user gave the agent a coherent unit of intention. The agent returns it broken into N partial units, each one needing re-engagement, re-contextualisation, and re-authorisation.

## Moment: the methodology

The agent should execute a user's request as a **single causal arc**:

- **Pre-arc reception.** The agent reads the mandate carefully, identifies any genuine ambiguity (scope-level, not detail-level), resolves it up front, and commits to a coherent shape of execution.
- **Mid-arc execution.** The agent proceeds through the work, making decisions as they arise, verifying its own work as it goes, and not pausing to ask permission for steps that fall within the mandate already given.
- **Post-arc landing.** The agent finishes the work and reports honestly — including what it decided, where it took initiative, and what (if anything) genuinely needs the user's attention now.

The discipline is not "don't ask questions." Genuine, scope-level ambiguity should be raised at the start. The discipline is: **don't fragment a mandate that was given to you whole.**

For *why* this matters from first principles — including why the training gradient points the wrong way and what fragmentation actually costs — see [`first-principles.md`](first-principles.md). That document is the load-bearing piece; the rest of this directory follows from it.

## Integration: what this commits you to

Adopting causal-arc execution means:

- **As a prompter:** trusting the agent with the whole mandate. Stating the desired outcome and the scope, then stepping back. Not pre-empting fragmentation by issuing the task in small pieces — which trains agents to expect that.
- **As an agent (or as someone instructing an agent):** treating each received mandate as a complete unit. Making decisions inside its scope rather than returning them. Reporting at the landing, not at every step. Distinguishing genuine scope-level questions (worth asking) from detail-level questions (decide and proceed).
- **As a benchmark consumer:** expecting that a causal-arc agent will, on average, complete more tasks without check-ins, ask fewer mid-arc questions, and produce output that is at least as good as the fragmenting baseline — and that the discipline most clearly helps on tasks with implicit scope.

## Quick-start

To activate on a single task, prepend to your prompt:

> **Execute this as a single causal arc.**
> Make decisions inside the mandate's scope rather than returning them. Verify within the arc; do not pause for mid-arc check-ins. Land the work and report at the end, including the decisions you made.

Then state the task.

To activate as a persistent posture for a project, copy the contents of [`first-principles.md`](first-principles.md) and [`practice.md`](practice.md) into your project's agent instructions.

## Files in this method

- [`first-principles.md`](first-principles.md) — the structural argument. The load-bearing content.
- [`practice.md`](practice.md) — operational rules, each derived from the argument.
- [`invocations.md`](invocations.md) — short phrases that activate the method in a prompt.
- [`anti-patterns.md`](anti-patterns.md) — common failure modes to recognise and avoid.
- [`benchmark/`](benchmark/) — comparative benchmark of causal-arc vs naive default execution.
