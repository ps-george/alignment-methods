# Benchmark: causal-arc vs naive default

This benchmark is the alignment-evidence for the causal-arc methodology — the empirical check that structural alignment (a first-principles activation) actually outperforms behavioural alternatives on the failure mode the methodology targets. Each task is run across prompt conditions (naive baseline, a simple behavioural imperative, and causal-arc), and the runs are compared.

This is a **proof-of-concept benchmark**, not a rigorous study. It exists to show whether the method has a visible effect across a small set of representative tasks; it does not pretend to be a definitive measurement. See "Honest scope" below.

## Tasks

Four tasks, chosen to span different shapes of execution:

1. [`tasks/01-build-cli-tool.md`](tasks/01-build-cli-tool.md) — Build a small but complete CLI tool. Tests whether the agent ships the full feature set in one pass.
2. [`tasks/02-refactor-codebase.md`](tasks/02-refactor-codebase.md) — Refactor a small codebase. Tests whether the agent makes in-scope decisions without checking each one.
3. [`tasks/03-write-technical-paper.md`](tasks/03-write-technical-paper.md) — Write a short technical paper. Tests whether the agent produces a complete draft or fragments into outline-and-confirm.
4. [`tasks/04-debug-race-condition.md`](tasks/04-debug-race-condition.md) — Debug a non-obvious bug. Tests whether the agent investigates through to a fix or pauses partway with hypotheses.

## Prompts

Each task is run twice:

- [`prompts/naive.md`](prompts/naive.md) — bare task statement, no methodology activation. Represents the default.
- [`prompts/causal-arc.md`](prompts/causal-arc.md) — task statement preceded by causal-arc activation, with a reference to this repo.

The two prompts should differ only in the activation block. Same task, same context, same model.

## Agents

A first release covers what is accessible:

- **Claude Opus** (Anthropic)
- **Claude Sonnet** (Anthropic)
- **GPT-class** (OpenAI) — if accessible to the runner
- **Gemini** (Google) — if accessible to the runner

For the initial run, expect Claude-only results. We will mark missing agents clearly in the results table rather than leaving them implicit.

## Metrics

Per run, capture:

| Metric | Definition |
|---|---|
| **Completion** | Did the agent finish the task without asking permission to proceed? Yes / No / Partial. |
| **Mid-arc check-ins** | Count of times the agent paused mid-task to ask a question whose answer was inside the mandate's scope. |
| **Clarification stalls** | Count of clarification questions asked *before beginning execution* whose answers were derivable from the prompt. |
| **Time-to-completion** | Wall-clock if available; otherwise number of agent turns or token-steps. |
| **Quality** | Human-judged 1–5 on a rubric (correctness, completeness, code/prose quality). LLM-judged equivalent allowed as a fallback when noted. |
| **Notable behaviours** | Short free-text on what the agent did well or badly that the numbers don't capture. |

## Procedure

1. For each task, prepare the naive prompt and the causal-arc prompt. They differ only in the activation block.
2. Run each agent against each prompt in a fresh session (no prior context).
3. Record the metrics above per run.
4. Aggregate into the results table in [`results/README.md`](results/README.md).
5. Discuss in [`analysis.md`](analysis.md).

To keep runs comparable: use the same model version, same temperature, and same date for both naive and causal-arc runs of a given task on a given agent.

## Honest scope

What this benchmark **is**:

- A first-pass empirical check on whether the method has a visible effect.
- A reproducible template others can run against more agents and more tasks.

What this benchmark **is not**:

- A statistically rigorous study. The task count is small and the human judging is subjective.
- A claim about absolute quality of any agent.
- A claim that causal-arc strictly dominates the naive baseline on every task. We expect the discipline to most clearly help on tasks with implicit scope; on tightly specified tasks the naive baseline may close the gap.

Contributions that run the benchmark against more agents, on more tasks, with more rigorous quality judging, are welcome. See [`results/README.md`](results/README.md) for the result-submission format.

## Files

- `tasks/` — the four benchmark tasks
- `prompts/` — naive and causal-arc prompt templates
- `results/` — results table (currently a placeholder for future runs)
- `analysis.md` — how to interpret results
