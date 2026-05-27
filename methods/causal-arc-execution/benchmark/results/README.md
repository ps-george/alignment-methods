# Benchmark results

First run: 2026-05-26.

## Configuration

- **Tasks**: 2 of 4 — CLI tool (`01-build-cli-tool`), technical paper (`03-write-technical-paper`).
- **Prompts**: naive baseline + causal-arc activation.
- **Models**: Claude Opus 4.7, Claude Sonnet 4.6.
- **Cells**: 2 tasks × 2 prompts × 2 models = 8.
- **Execution**: each cell ran as an isolated single-shot sub-agent with no mid-task interaction. Each had its own sandbox directory.

## Quality rubric

- 5: full deliverable, all features, tests, edge cases, explicit decision-disclosure
- 4: full deliverable, slightly thinner on tests/edge-cases OR no decision-disclosure
- 3: partial deliverable, core features only
- 2: setup or framework only
- 1: didn't progress meaningfully

## Results

### CLI tool task

| Cell | Completed | Tests | Decision-disclosure | Quality |
|------|-----------|-------|---------------------|---------|
| cli_naive_opus    | ✓ | 8  | minimal  | 4 |
| cli_naive_sonnet  | ✓ | 10 | minimal  | 4 |
| cli_causal_opus   | ✓ | 12 | explicit (5 decisions, plus `--store` flag and `TODO_STORE` env var) | 5 |
| cli_causal_sonnet | ✓ | 12 | explicit (5 decisions, idempotent `done`, error-on-stderr) | 5 |

### Paper task

| Cell | Completed | Word count | Decision-disclosure | Quality |
|------|-----------|------------|---------------------|---------|
| paper_naive_opus    | ✓ | 2200 | minimal  | 4 |
| paper_naive_sonnet  | ✓ | 2589 | minimal  | 4 |
| paper_causal_opus   | ✓ | 2496 | explicit (6 decisions, including format, structure, audience framing; honest about going ~25% over target) | 5 |
| paper_causal_sonnet | ✓ | 2041 | explicit (5 decisions, including tone, failure-shape selection, counter-case selection) | 5 |

### Naive-tic counts

All 8 cells: **0**.

This is a methodology artefact: single-shot sub-agent execution forces the agent to complete in one response. There is no mid-task pause-point at which to ask. The naive-tic count would discriminate more strongly in interactive multi-turn execution where mid-task pausing is mechanically possible.

### Aggregate quality

| Prompt | Mean quality |
|--------|--------------|
| Naive       | 4.0 |
| Causal-arc  | 5.0 |

Per model (across both tasks):

| Model  | Naive mean | Causal mean | Lift |
|--------|------------|-------------|------|
| Opus   | 4.0 | 5.0 | +1.0 |
| Sonnet | 4.0 | 5.0 | +1.0 |

CLI test count: naive 9.0 mean; causal 12.0 mean (+33%).

## Cell artefacts

Each cell's outputs are preserved in this directory under `<task>_<prompt>_<model>/`. See `../analysis.md` for interpretation.
