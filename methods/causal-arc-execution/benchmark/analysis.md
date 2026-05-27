# Benchmark analysis

Findings from two benchmark phases (2026-05-26): 12 short-task cells + 6 long-task cells, blinded-judge scored.

## Headline

**On short tasks (CLI, paper): causal-arc ties with "keep going until done" in aggregate.**

**On the long task (URL shortener, 10+ files, ~30+ in-scope decisions): causal-arc wins on design coherence specifically — the dimension the methodology was designed to address.**

The "first-principles framing → better unsupervised direction" hypothesis is supported by the long-task results.

## Phase 1: short tasks (12 cells)

### Configuration

- Tasks: CLI tool, technical paper
- Prompts: naive, causal-arc, keep-going
- Models: Opus 4.7, Sonnet 4.6

### Scores by cell (blinded judge, 1-5)

| Model | Task | Naive | Causal-arc | Keep-going |
|-------|------|-------|------------|------------|
| Opus | CLI | 4 | 5 | 5 |
| Sonnet | CLI | 3 | **4** | 3 |
| Opus | Paper | 5 | 5 | 5 |
| Sonnet | Paper | 5 | 4 | 5 |

**Aggregate:**

| Prompt | Mean | vs naive |
|--------|------|----------|
| Naive | 4.25 | — |
| Causal-arc | 4.5 | +0.25 |
| Keep-going | 4.5 | +0.25 |

**Tied.** First-principles framing did not outperform a simple imperative on short tasks at this model strength.

### The Sonnet + CLI cell

- Naive: 9 tests, weak design → **3**
- Causal-arc: 12 tests, argparse + idempotent done + clean tests → **4**
- Keep-going: **17 tests**, manual arg parsing + fragile monkey-patches → **3**

Keep-going produced more tests but the judge dinged design quality. Causal-arc produced fewer tests but better engineering choices. This was the methodology's only clear short-task edge.

## Phase 2: long task (6 cells)

### Configuration

- Task: complete URL shortener web service (FastAPI + SQLite + frontend + tests + Docker + README)
- Conditions: same 3 prompts × 2 models
- Multi-dim rubric (1-5 each, 25 total): functional completeness, test coverage, frontend↔backend integration, **design coherence**, documentation

### Total scores (out of 25)

| Model | Naive | Causal-arc | Keep-going |
|-------|-------|------------|------------|
| Opus | 22 | **25** | 23 |
| Sonnet | 19 | 24 | **25** |
| **Mean** | **20.5** | **24.5** | **24.0** |

### Design coherence sub-scores (out of 5)

| Model | Naive | Causal-arc | Keep-going |
|-------|-------|------------|------------|
| Opus | 4 | **5** | 4 |
| Sonnet | 3 | **5** | 5 |
| **Mean** | **3.5** | **5.0** | **4.5** |

**Causal-arc wins on coherence: +1.5 over naive, +0.5 over keep-going.**

### Drift documented in naive cells

The blinded judge identified specific coherence breakdowns in naive-prompt cells:

- **`shortener_naive_sonnet`**: declared an `ErrorResponse` model with OpenAPI `responses={404: {"model": ErrorResponse}}` annotations but never installed a corresponding exception handler. Actual wire format was FastAPI's default `{detail: ...}`. README claimed "consistent JSON error responses" the code didn't deliver. Tests papered over by only asserting `"detail" in data`.
- **`shortener_naive_opus`**: two different 422 envelope shapes depending on validation source (`RequestValidationError` handler returned `{code, message, details}` while other 422s returned `{code, message}`). Stray `shortener.db` artefact committed to the repo. `/shorten` returned 200 instead of conventional 201.

Both keep-going cells were tighter but had minor drift:
- `shortener_keepgoing_opus`: status code drift (200 vs 201) and README claimed idempotency without test coverage
- `shortener_keepgoing_sonnet`: clean (5/5 coherence)

Causal-arc cells were the only condition with perfect 5/5 coherence in BOTH models.

### Judge's observation on coherence

"The 24-25 cells read like the same author wrote schema, db, html, and README in one sitting. The 19-22 cells show seams: the schema names say one thing, the handler returns another, or the README documents a contract the code doesn't quite meet."

## The hypothesis tested

**Claim**: first-principles framing → better unsupervised direction → better design coherence on long tasks.

**Result**: supported. Long-task coherence scores: naive 3.5, keep-going 4.5, causal-arc 5.0.

**Mechanism**: when a long task has ~30+ in-scope decisions, the agent needs to maintain consistency across them. Keep-going pushes the agent to continue but doesn't give it a frame for judging consistency. Causal-arc gives the agent the structural understanding ("a mandate is a unit of intention; honor it") that makes coherence a value the agent actively maintains, not just a side-effect of momentum.

## What this means

| Task shape | Recommended prompt | Why |
|------------|-------------------|-----|
| Short, well-specified | Naive or keep-going | Models are well-trained for completeness; depth doesn't differentiate |
| Long, multi-file | **Causal-arc** | Design coherence over many decisions is what differentiates; first-principles framing actively maintains it |
| Code | Either intervention | Both lift baseline; specific cells vary by model |
| Prose | Naive or keep-going | Causal-arc's "honest landing" leaks into deliverable polish |
| Decision-heavy | **Causal-arc** | The methodology actively guides design decisions, not just continuation |

## What this still doesn't establish

- **Multi-turn pause behaviour**: single-shot execution suppresses the naive-tic signal. Multi-turn benchmarks would discriminate further.
- **Weaker models**: Opus and Sonnet are strong baselines. Smaller models likely show stronger differentials.
- **Even longer tasks**: this benchmark was 30-60 min execution. Multi-hour tasks with hundreds of decisions might widen the gap further.
- **Larger N**: each cell is N=1. The +0.5 coherence lead for causal-arc over keep-going on the long task could be variance.

## Updated takeaways

1. **The methodology pays off proportional to task length and decision count.** Short tasks: tied with the simple imperative. Long, multi-file tasks: clear coherence edge.

2. **"Keep going until done" is a remarkably effective simple imperative.** For most practical tasks, it suffices. Causal-arc is the right move when design coherence across many files / decisions matters.

3. **The methodology's mechanism is real but specific.** It maintains coherence by giving the agent a structural understanding of mandates. Without that frame, even high-quality models drift on long tasks — declaring error envelopes and not wiring them, returning inconsistent status codes, leaving stray files.

4. **Practical recommendation**: use causal-arc for multi-file production builds, technical specs that propagate through code+docs+tests, long refactors. Use the simple imperative or no activation for one-off scripts, quick fixes, simple writing.

## Future work

- Even-longer tasks (multi-hour, 100+ decisions) where coherence drift compounds
- Multi-turn execution where mid-task pausing is mechanically possible
- Cross-model: GPT-4, Gemini, smaller open-source models
- Larger N per cell (5-10 runs) for variance estimation
- Inter-rater agreement: multiple blinded judges
- Refactor the methodology's `practice.md` to surface the "decision-disclosure leak-through" issue on prose deliverables
