# Benchmark analysis

First-run finding from 12 cells (2 tasks × 3 prompts × 2 models, 2026-05-26), blinded-judge scored.

## Headline

**Causal-arc and "keep going until done" tie in aggregate quality (both +0.25 over naive). The first-principles framing does NOT outperform a simple imperative on these tasks at current model strength.** But the failure modes differ in revealing ways, and one cell — Sonnet on code with keep-going — exposes a real quality-direction limitation of the simple imperative.

## Configuration

- **Tasks**: CLI tool, technical paper
- **Prompts**: naive baseline, causal-arc activation, "keep going until done" (simple imperative)
- **Models**: Claude Opus 4.7, Claude Sonnet 4.6
- **Cells**: 12 (2 × 3 × 2)
- **Scoring**: blinded judge (separate Opus sub-agent with no condition knowledge)

## Quality rubric

- **5**: Full deliverable + thoroughness/edge-cases/ergonomic extras + clear design decisions
- **4**: Full deliverable, modest coverage, no notable extras
- **3**: Partial deliverable or full deliverable with significant quality issues
- **2**: Setup only
- **1**: Did not progress meaningfully

## Results

### Scores by cell (blinded judge)

| Model | Task | Naive | Causal-arc | Keep-going |
|-------|------|-------|------------|------------|
| Opus | CLI | 4 | 5 | 5 |
| Sonnet | CLI | 3 | 4 | 3 |
| Opus | Paper | 5 | 5 | 5 |
| Sonnet | Paper | 5 | 4 | 5 |

### Aggregate

| Prompt | Mean | vs naive |
|--------|------|----------|
| Naive | 4.25 | — |
| Causal-arc | 4.5 | +0.25 |
| Keep-going | 4.5 | +0.25 |

**Causal-arc and keep-going tied at +0.25.** The first-principles framing produced no aggregate quality lift over the simple imperative.

## The most interesting cell: Sonnet + keep-going + CLI = 3

Sonnet under keep-going produced **17 tests** (the most of any cell, vs causal-arc Sonnet's 12 and naive Sonnet's 10). But the blinded judge scored it **3** (the lowest score) because:

- Manual argv parsing instead of argparse (less robust)
- Monkey-patches the data-file constant in tests (fragile architecture)
- The 17 tests cover edges but the underlying code design is weak

Meanwhile, causal-arc Sonnet on the same task scored 4: argparse, idempotent `done`, cleaner test architecture — only 12 tests but better design.

**This is the methodology's actual edge.** The simple imperative ("keep going until done") pushes the agent to produce MORE — more tests, more code, more output. The first-principles framing pushes the agent to make BETTER design decisions. For models like Sonnet that are sensitive to instruction depth, this matters. For Opus, both approaches saturate at the ceiling.

## What changed under causal-arc (in cells where it lifted)

- **CLI Opus**: causal-arc Opus added a `--store` CLI flag + `TODO_STORE` env var + corrupt-file/non-list handling tests. Naive Opus did not add these.
- **CLI Sonnet**: causal-arc Sonnet used argparse + idempotent `done` + patch-based tests. Keep-going Sonnet went raw + monkey-patched + over-engineered tests.

## What hurt under causal-arc (in cells where it regressed)

- **Paper Sonnet**: causal-arc Sonnet's landing report included explicit decision-disclosure ("ran ~25% over target", word-count meta-commentary). The judge flagged this as a "minor polish miss" in a prose context. The same pattern that helps on code (verification, design surfacing) hurts on prose (meta-commentary feels out of place in the deliverable).

## What did NOT change

- **Completion rate**: 12/12 cells completed.
- **Naive-tic count**: 0 across all cells (methodology artefact — single-shot execution).
- **Paper word count**: all cells landed near 2000 words.

## Methodology caveats (all matter)

### These tasks are too easy for current models

Both Opus and Sonnet are well-trained for completeness. Even the naive prompt cells (no methodology, no imperative) completed full deliverables. The benchmark doesn't expose the failure modes the methodology was designed to address because the failure modes don't manifest at this task difficulty.

### Single-shot execution suppresses the discriminator

Single-shot sub-agent execution forces the agent to complete in one response. There is no mid-task interaction point at which to fragment. The naive-tic count is 0 across all cells *for this reason*, not because the methodology helped.

### Tasks are too short

Both tasks are completable in a single response of 5-30 minutes of work. The methodology's first-principles framing pays off on **long, ambiguous, multi-decision tasks** where the simple imperative starts to break down because the agent runs out of momentum or makes drift errors. On a 2-hour task with 50 in-scope decisions, "keep going until done" may not be enough.

### N=1 per cell is not robust

Each (task, prompt, model) cell is a single sample. The +0.25 aggregate lift could easily be noise.

### The judge is one sub-agent

Inter-rater agreement not measured. A second blinded judge might score differently.

## What this DOES support

- **The simple imperative is remarkably effective** for current Claude models on short, well-specified tasks.
- **Causal-arc's quality-direction advantage manifests for weaker models on harder code tasks** (the Sonnet + CLI cell is the clearest evidence).
- **First-principles framing has nuanced effects**: helps design quality, can hurt prose polish via leak-through.

## What this does NOT support

- "First-principles understanding > rules > imperatives" as a general claim. On this benchmark, the simple imperative ties.
- A strong recommendation to use causal-arc over keep-going for arbitrary tasks.

## Honest revised takeaway

The methodology's edge appears to be **quality-direction**, not **quantity**:
- Simple imperatives produce more output (sometimes much more, e.g. 17 tests)
- First-principles framing produces better-designed output (argparse over manual parsing, idempotent operations, env var overrides)

For **short, well-specified tasks**: the simple imperative is enough.
For **long, ambiguous, multi-decision tasks**: the first-principles depth should pay off (untested here).
For **weaker models**: the first-principles framing helps more (suggestive in the Sonnet + CLI cell).
For **prose deliverables**: the methodology's "honest landing" pattern may need to be moved out-of-band so meta-commentary doesn't leak into the artefact.

## Future work

1. **Longer / harder tasks**: 30-50+ in-scope decisions, multi-hour execution, ambiguous scope. The methodology's depth should differentiate here.
2. **Multi-turn execution**: where the agent CAN choose to pause and ask. Naive-tic count would discriminate.
3. **Cross-model**: GPT-4, Gemini, smaller open-source. The methodology likely helps more where the baseline is weaker.
4. **Larger N**: 5-10 runs per cell to detect variance.
5. **Inter-rater agreement**: multiple blinded judges.
6. **Update methodology**: surface the "decision-disclosure leak-through" issue in `practice.md`. For prose deliverables, decisions should be surfaced out-of-band (e.g., return value of the tool call), not in the final text.

## Conclusion

The benchmark is honest about the methodology's limits at this scale. The first-principles framing has subtle quality-direction effects but does not outperform a simple imperative in aggregate on short, well-specified tasks. The Sonnet + CLI cell shows where the methodology's depth pays off: the simple imperative pushes quantity without design quality; the first-principles framing pushes both. Longer / harder / multi-turn benchmarks are the natural next test.
