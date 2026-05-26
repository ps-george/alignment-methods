# agent-methods

A library of methodologies for working with AI agents effectively.

Each method here is a discipline you can teach an agent — or invoke when prompting one — to change how it executes. The library is opinionated about how methods are written: they must work by giving the agent **first-principles understanding**, not by stacking surface-level rules.

## Why this library exists

Most failure modes you see in AI agent work — fragmented execution, excessive check-ins, defaulting to a minimum-viable output, scope-truncation, over-asking — are not random. They are predictable consequences of how current models are trained. Telling an agent "don't do that" works briefly and then erodes; the training gradient pulls the behaviour back.

What holds is when the agent **understands why** the discipline matters from the inside. A model that has internalised the structural argument for a discipline applies it even under pressure, because the discipline now lives in its model of the world rather than as a fragile surface instruction.

This library collects methods that meet that bar.

## Current methods

| Method | Status | What it addresses |
|---|---|---|
| [Causal-arc execution](methods/causal-arc-execution/) | v0.1 | Fragmented execution, mid-arc check-ins, MVP-default behaviour |

More methods will be added over time. Each will follow the same format (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## Quick start

If you just want to invoke the first method on a task, paste this into your agent prompt:

> Execute this as a single causal arc. Make decisions, don't ask. Verify within the arc. No mid-arc checkpoints. Build the whole thing through to a landing.
>
> [your task here]

For why this works, read [`methods/causal-arc-execution/first-principles.md`](methods/causal-arc-execution/first-principles.md). For when to use which phrasing, read [`methods/causal-arc-execution/invocations.md`](methods/causal-arc-execution/invocations.md).

## Philosophy in one paragraph

A methodology is not a rule. A rule is something an agent obeys; a methodology is something an agent understands. Rules can be rationalised away under pressure or eroded by training gradients that point the other way. Understanding holds because it changes the agent's model of what it is doing. Every method in this library is written first as an argument for why the discipline matters, and only second as an operational prescription. See [`philosophy.md`](philosophy.md) for the longer version.

## Navigation

- [`philosophy.md`](philosophy.md) — why this library exists and what makes a good method
- [`methods/causal-arc-execution/`](methods/causal-arc-execution/) — the first method
- [`methods/causal-arc-execution/benchmark/`](methods/causal-arc-execution/benchmark/) — comparative benchmark
- [`examples/`](examples/) — methods in real use
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add a method

## Contribute

If you have a discipline you apply to AI agents that meets the first-principles bar — that is, you can argue from structure why it matters, not just assert it as a rule — open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for the format.

## License

MIT. See [LICENSE](LICENSE).

## Author

George Morgan
