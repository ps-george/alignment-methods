# Contributing

This library accepts new methods that meet the first-principles bar described in [`philosophy.md`](philosophy.md).

## Format

Each method lives at `methods/<method-name>/` and contains, at minimum:

```
methods/<method-name>/
├── README.md            # Summary: setup, moment, integration
├── first-principles.md  # The structural argument (load-bearing)
├── practice.md          # Operational rules, derived from first-principles
├── invocations.md       # Prompt phrases that activate the method
└── anti-patterns.md     # Failure modes to avoid
```

A `benchmark/` subdirectory is encouraged but not required for an initial submission. See `methods/causal-arc-execution/benchmark/` for the template.

## The bar

Before submitting, confirm:

1. **There is a real failure mode.** The method addresses a behaviour you have observed degrade agent output across multiple sessions or agents, not a one-off.
2. **The argument is structural.** Your first-principles document explains *why* the discipline matters from the shape of the situation, not from authority or "best practice".
3. **The practice follows.** The rules in `practice.md` are derivable from `first-principles.md`. If a reader internalised only the first-principles content, the rules would feel like consequences, not surprises.
4. **No mysticism.** The method works because of something legible. If you find yourself unable to explain why it works, it isn't ready.

## Style

- Plain prose. Avoid jargon unless you define it.
- Argue, don't assert. Where you make a claim, show why.
- Keep each file focused on one job. README summarises; first-principles argues; practice prescribes; invocations lists; anti-patterns warns.

## Process

1. Fork, branch.
2. Add your method directory with the files above.
3. Add a row to the methods table in the top-level `README.md`.
4. Open a PR. Expect feedback focused on whether the first-principles content carries the weight.

## License

By contributing, you agree your contribution is released under the MIT License.
