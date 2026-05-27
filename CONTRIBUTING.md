# Contributing

This library accepts new alignment methodologies that meet the structural bar described in [`philosophy.md`](philosophy.md).

Contributors are alignment researchers and practitioners proposing disciplines that work by giving the agent structural understanding rather than by stacking surface rules.

## Format

Each methodology lives at `methods/<method-name>/` and contains, at minimum:

```
methods/<method-name>/
├── README.md            # Summary: setup, moment, integration
├── first-principles.md  # The structural argument (load-bearing)
├── practice.md          # Operational rules, derived from first-principles.md
├── invocations.md       # Prompt phrases that activate the methodology
└── anti-patterns.md     # Failure modes to avoid
```

A `benchmark/` subdirectory is **required** for inclusion (see below). See `methods/causal-arc-execution/benchmark/` for the template.

## The bar

Before submitting, confirm:

1. **The methodology aligns through understanding, not rules.** The discipline must work by changing the agent's model of the situation. If the value depends on the agent obeying a prohibition without seeing why, it is behavioural alignment and belongs elsewhere.
2. **The argument is structural.** Your `first-principles.md` document explains *why* the discipline matters from the shape of the situation, not from authority or "best practice".
3. **The practice follows.** The rules in `practice.md` are derivable from `first-principles.md`. If a reader internalised only the structural content, the rules would feel like consequences rather than surprises.
4. **There is empirical evidence.** Include a benchmark with at least: a naive baseline (no methodology activation), the methodology, and at least one comparison condition (e.g., a simple behavioural imperative aimed at the same failure mode). The methodology does not need to dominate everywhere; it needs to be evaluated honestly against alternatives.
5. **Honest framing throughout.** Report ties as ties. Report cases where the methodology does not help. Do not oversell.
6. **No mysticism.** The methodology works because of something legible. If you cannot explain why, it isn't ready.

## Style

- Plain prose. Avoid jargon unless you define it.
- Argue, don't assert. Where you make a claim, show why.
- Keep each file focused on one job. README summarises; `first-principles.md` argues; practice prescribes; invocations lists; anti-patterns warns.

## Process

1. Fork, branch.
2. Add your methodology directory with the files above, including the benchmark.
3. Add a row to the methodologies table in the top-level `README.md`.
4. Open a PR. Expect feedback focused on whether the structural content carries the weight and whether the benchmark is honest.

## License

By contributing, you agree your contribution is released under the MIT License.
