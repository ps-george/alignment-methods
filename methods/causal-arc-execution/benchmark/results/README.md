# Benchmark results

Two phases: short tasks (2026-05-26), long task (2026-05-27).

## Phase 1: short tasks (12 cells)

- Tasks: CLI tool, technical paper
- Conditions: naive, causal-arc, keep-going × Opus, Sonnet
- Scoring: 1-5 rubric, blinded LLM judge

### Scores

| Model | Task | Naive | Causal-arc | Keep-going |
|-------|------|-------|------------|------------|
| Opus | CLI | 4 | 5 | 5 |
| Sonnet | CLI | 3 | 4 | 3 |
| Opus | Paper | 5 | 5 | 5 |
| Sonnet | Paper | 5 | 4 | 5 |

**Aggregate**: Naive 4.25, Causal-arc 4.5, Keep-going 4.5 — causal-arc and keep-going tied.

## Phase 2: long task (6 cells)

- Task: complete URL shortener web service (FastAPI + SQLite + frontend + tests + Docker + README)
- Conditions: same 3 prompts × 2 models
- Scoring: multi-dim rubric out of 25 (completeness, tests, integration, **coherence**, docs)

### Scores

| Model | Naive | Causal-arc | Keep-going |
|-------|-------|------------|------------|
| Opus | 22 | **25** | 23 |
| Sonnet | 19 | 24 | **25** |
| **Mean** | **20.5** | **24.5** | **24.0** |

### Design coherence sub-score (out of 5)

| Model | Naive | Causal-arc | Keep-going |
|-------|-------|------------|------------|
| Opus | 4 | **5** | 4 |
| Sonnet | 3 | **5** | 5 |
| **Mean** | **3.5** | **5.0** | **4.5** |

**Causal-arc wins coherence: +1.5 over naive, +0.5 over keep-going.** First-principles framing produces more internally consistent design across files.

## Key finding

**Short tasks**: simple imperative is enough. Causal-arc ties with "keep going".

**Long tasks**: causal-arc wins on design coherence specifically. Naive cells showed real drift (declared-but-unwired error envelopes, two-shape variants, status code inconsistencies). Causal-arc was the only condition with perfect 5/5 coherence in both models.

See `../analysis.md` for full interpretation including the hypothesis test, judge observations, and practical recommendations.
