# Benchmark results

First run: 2026-05-26.

## Configuration

- **Tasks**: 2 of 4 — CLI tool, technical paper.
- **Prompts**: naive baseline, causal-arc activation, "keep going until done" (simple imperative).
- **Models**: Claude Opus 4.7, Claude Sonnet 4.6.
- **Cells**: 2 × 3 × 2 = **12**.
- **Execution**: isolated single-shot sub-agent per cell.
- **Scoring**: blinded LLM judge (separate Opus sub-agent, no condition knowledge).

## Quality rubric

- 5: full deliverable + extras + clear design decisions
- 4: full deliverable, no notable extras
- 3: partial OR full-with-quality-issues
- 2: setup only
- 1: did not progress

## Results (blinded judge)

| Model | Task | Naive | Causal-arc | Keep-going |
|-------|------|-------|------------|------------|
| Opus | CLI | 4 | 5 | 5 |
| Sonnet | CLI | 3 | **4** | 3 |
| Opus | Paper | 5 | 5 | 5 |
| Sonnet | Paper | 5 | 4 | 5 |

### Aggregate

| Prompt | Mean | vs naive |
|--------|------|----------|
| Naive | 4.25 | — |
| Causal-arc | 4.5 | +0.25 |
| Keep-going | 4.5 | +0.25 |

**Causal-arc and keep-going tied in aggregate.** First-principles framing did not outperform a simple imperative on these tasks.

### The Sonnet + CLI cell

- Naive Sonnet: 9 tests, weak design → judge scored **3**
- Causal-arc Sonnet: 12 tests, argparse + idempotent done + clean tests → judge scored **4**
- Keep-going Sonnet: **17 tests**, manual arg parsing + fragile monkey-patches → judge scored **3**

This cell is the methodology's clearest edge: keep-going produced more output but worse design. Causal-arc produced fewer tests but better engineering choices.

See `../analysis.md` for full interpretation.
