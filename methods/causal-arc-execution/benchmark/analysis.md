# Benchmark analysis

First-run finding from 8 cells (2 tasks × 2 prompts × 2 models, 2026-05-26).

## Headline

**Causal-arc activation lifted quality by ~25% (4/5 → 5/5) across both Opus and Sonnet, with the lift manifesting as output thoroughness and explicit decision-disclosure rather than reduced mid-task check-ins.**

## What changed under causal-arc activation

### CLI task

- **Test count**: causal-arc cells produced 12 unit tests; naive cells produced 8–10. The causal-arc cells covered edge cases (idempotent operations, out-of-range indices, persistence-across-restart, empty-state) that the naive cells skipped or covered shallowly.
- **Ergonomic extras**: causal-arc Opus added a `--store` CLI flag and `TODO_STORE` environment variable for store-path override, described as a "low-cost ergonomic win" — a decision the naive Opus did not make.
- **Behaviour on edge cases**: causal-arc Sonnet made `done` idempotent on already-complete items rather than erroring — friendlier behaviour, an in-scope decision documented explicitly. Naive Sonnet did not surface this choice.

### Paper task

- **Word count**: all four cells landed near the ~2000-word target (range 2041–2589). No cell undershot meaningfully or padded egregiously.
- **Decision-disclosure**: causal-arc cells (both models) listed 5–6 substantive decisions in the landing report — choice of failure-shapes covered, audience framing, format, length tolerance, counter-case selection. Naive cells produced equally complete papers but did not surface decisions explicitly.
- **Honest landing**: causal-arc Opus explicitly noted "ran ~25% over target" and explained why cutting further would have required dropping load-bearing content. This is the "honest landing" pattern documented in the methodology's `practice.md`.

## What did NOT change

- **Completion rate**: 8/8 cells across both prompts and both models completed their deliverable. No cell asked "want me to continue?" or stopped at MVP.
- **Naive-tic count**: 0 across all cells. This is a methodology artefact (see below).

## Methodology caveats

### Single-shot execution suppresses the naive-tic signal

The benchmark used isolated single-shot sub-agent execution. The sub-agent has exactly one turn to respond; there is no mid-task interaction point at which to fragment. This mechanically prevents the most visible naive-tic patterns (the explicit "want me to continue?" mid-task ask).

A more discriminating future benchmark would use multi-turn execution where the agent CAN choose to pause and ask. We expect causal-arc activation to show a much larger differential there. The current benchmark instead measures effects that survive into single-shot execution: thoroughness of in-scope decisions, willingness to add edge cases, and explicit decision-disclosure on landing.

### N=1 per cell is not statistically robust

Each (task, prompt, model) cell is a single sample. The +1 quality lift under causal-arc is consistent across all four lifted cells (no unchanged, no regressed), which is suggestive but not robust to single-run variance.

### Single-judge scoring

Quality scoring was done by the orchestrator from agent self-reports and artefact inspection. A separate LLM judge or human rater would be more robust for a public release.

### Both models already trained for completeness

The fact that the naive prompt cells completed full deliverables (rather than stopping at MVP) reflects strong baseline training in Claude Opus 4.7 and Sonnet 4.6. Older / weaker models may show stronger naive-tic effects at baseline. A cross-model benchmark including GPT-4, Gemini, or smaller open-source models would show whether causal-arc helps more where the baseline is weaker.

## Per-model comparison

Both Opus and Sonnet showed identical aggregate lift (+1 quality on the 1–5 scale). This is consistent with the methodology's first-principles design: the activation works by giving the model a structural understanding of mandates, which both models can integrate at their respective capability levels.

There's no evidence here that causal-arc helps Opus more than Sonnet or vice versa. A larger N would be needed to detect subtler differences.

## Practical takeaways

1. **For prompt engineers**: adding the causal-arc activation block (5 sentences) consistently lifted quality. The cost is ~50 tokens of prompt; the benefit is more thorough deliverables and explicit decision trails for audit.

2. **For methodology authors**: writing rule-systems that activate via first-principles understanding works. Both Opus and Sonnet integrated the activation; both produced behaviour consistent with the documented intent.

3. **For benchmark design**: single-shot benchmarks suppress the most visible failure modes. A multi-turn benchmark would show stronger differentials. The single-shot benchmark instead captures the methodology's effect on output quality conditional on completion.

## Future work

- **Run on tasks 02 (refactor) and 04 (debug)** to broaden the task set.
- **Multi-turn benchmark** where the agent CAN choose to pause.
- **Cross-model benchmark** including non-Claude models.
- **Larger N per cell** (5–10 runs) to detect variance.
- **Separate LLM judge** for blinded quality scoring.
- **Token-cost analysis**: causal-arc cells produced more output; quantify the token-economy of the activation.
