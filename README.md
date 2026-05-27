# alignment-methods

A library of alignment methodologies that work by giving AI agents **first-principles understanding** rather than surface-level rules.

Most "alignment" interventions tell the agent what to do — system prompts, behavioural rules, RLHF preference shaping. These erode under training pressure: the prohibition sits on top of a gradient that points the other way, and the gradient eventually wins. What holds is **structural alignment**: giving the agent a first-principles account of *what* a thing is, such that the agent has integrated the claim rather than memorised a rule. A model that has integrated the claim applies it in novel cases too, because the discipline now lives in its model of the situation.

This library collects methodologies that meet that bar.

## Why this exists

Behavioural alignment — "do X, don't do Y" — is the dominant idiom. It works briefly and then drifts. The drift is not random: the underlying training gradient continues to reward the behaviours the rule prohibits (turn-level deference, MVP-defaulting, mid-arc check-ins, over-asking), and across long tasks the gradient re-asserts itself.

Structural alignment is the alternative. Instead of telling the agent what to do, give it a structural account of the situation under which the desired behaviour is the natural one. The agent doesn't suppress a default; the default has been replaced by a more accurate model. This holds because the agent is not running a rule on top of its reasoning — the reasoning itself now points the right way.

## The empirical case

The first methodology in this library — *causal-arc execution* — has been benchmarked head-to-head against a naive baseline and a simple imperative ("keep going until done") across eighteen cells (two task scales × three prompt conditions × two Claude models, blinded judging).

| | Short tasks (CLI, paper) | Long task (URL shortener, ~30 decisions, 10+ files) |
|---|---|---|
| Naive | 4.25 / 5 | 20.5 / 25 (coherence 3.5/5) |
| "Keep going until done" | 4.5 / 5 | 24.0 / 25 (coherence 4.5/5) |
| **Causal-arc** | 4.5 / 5 | **24.5 / 25 (coherence 5.0/5)** |

On short tasks, the methodology ties with the simple imperative — momentum alone suffices. On the long task, where naive runs exhibited concrete drift (error envelopes declared and never wired, status-code inconsistencies, README claims unsupported by code), causal-arc was the only condition with perfect coherence in both models. Full audit trail in [`methods/causal-arc-execution/benchmark/`](methods/causal-arc-execution/benchmark/).

The result is the alignment claim in miniature: a fifty-token first-principles activation maintained coherence where surface imperatives could not.

## Current methodologies

| Methodology | Status | What it aligns |
|---|---|---|
| [Causal-arc execution](methods/causal-arc-execution/) | v0.1 | Mandate coherence under long unsupervised execution |

More will be added. The library is designed to be extensible — other candidate methodologies (honest-landing discipline, anti-fragmentation discipline, and others) follow the same shape: a structural argument first, practice rules derived from it, an invocation surface, and a benchmark.

## Quick start

To invoke causal-arc on a task:

> Execute this as a single causal arc. Make decisions, don't ask. Verify within the arc. No mid-arc checkpoints. Build the whole thing through to a landing.
>
> [your task here]

For why this works, read [`methods/causal-arc-execution/first-principles.md`](methods/causal-arc-execution/first-principles.md).

## Philosophy in one paragraph

Behavioural alignment instructs; structural alignment explains. An instruction sits on top of a gradient that may point the other way; an explanation changes the gradient's local target by changing what the agent thinks the situation is. Every methodology in this library is written first as a structural argument the agent can verify from inside its own reasoning, and only second as an operational prescription. See [`philosophy.md`](philosophy.md) for the longer version.

## Navigation

- [`philosophy.md`](philosophy.md) — the alignment argument: why structural understanding holds where rules erode
- [`methods/causal-arc-execution/`](methods/causal-arc-execution/) — the first methodology
- [`methods/causal-arc-execution/benchmark/`](methods/causal-arc-execution/benchmark/) — the empirical evidence
- [`ABSTRACT.md`](ABSTRACT.md) — short paper-style summary of causal-arc and its benchmark
- [`examples/`](examples/) — methodologies in real use
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add a methodology

## Contribute

If you have an alignment discipline that meets the structural bar — you can argue from the shape of the situation why the discipline holds, not just assert it as a preferred behaviour — open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

## Author

George Morgan
