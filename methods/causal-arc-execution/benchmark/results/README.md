# Results

Benchmark results will be populated here as runs are performed. This file is a placeholder with the result-submission format.

## Status

No runs recorded yet. This release establishes the methodology and tasks; results from a first run are expected to follow.

## Results table format

Each row is one (agent, task, condition) tuple. Conditions: `naive` or `causal-arc`.

| Date | Agent | Model version | Task | Condition | Completion | Mid-arc check-ins | Clarification stalls | Time | Quality (1-5) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| _yyyy-mm-dd_ | _Claude Opus_ | _claude-opus-4-x_ | _01_ | _naive_ | _Yes / No / Partial_ | _N_ | _N_ | _wall-clock or turns_ | _1-5_ | _short notes_ |

A complete run for one agent covers eight rows: four tasks × two conditions.

## Submitting results

Open a PR adding rows to the table above. Include in the PR description:

- A link to or transcript dump of each run.
- Notes on judging — especially how the quality score was assigned (human rubric or LLM-judged).
- Any deviations from the procedure in [`../README.md`](../README.md).

Transcripts can live under `results/runs/<date>-<agent>/`. Keep them readable — at minimum the prompt and the final agent output; ideally the full transcript including any mid-arc questions.

## Expected shape of results

See [`../analysis.md`](../analysis.md) for how to interpret outcomes, including the prediction that causal-arc effects will be largest on tasks with implicit scope (Task 02, Task 04) and somewhat smaller on tasks with tight specification.
