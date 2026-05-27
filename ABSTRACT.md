# Causal-Arc Execution: An Alignment Methodology

### Structural alignment through comprehension, not compliance — with empirical evidence

---

**The problem.** Long-task agent output degrades through drift: declared error envelopes never get wired, status codes vary across endpoints, README claims diverge from what the code ships. This is not a capability ceiling — it's a *coherence* failure that the standard fix ("keep going until done") doesn't address. Momentum is not direction.

**The methodology.** *Causal-arc execution* gives the agent a structural understanding of what a mandate IS: a complete unit of intention carrying outcome, scope, and a delegation of trust. Fragmenting that unit into mid-arc check-ins degrades all three. The activation is fifty tokens of prompt. The mechanism is structural understanding the agent integrates and applies to novel in-scope decisions as they arise — not a list of rules it can rationalise around.

**The empirical case.** Blinded benchmark, eighteen cells across two task scales, three prompt conditions × two models (Claude Opus 4.7 and Sonnet 4.6):

| | Short tasks (CLI, paper) | Long task (URL shortener, ~30 decisions, 10+ files) |
|---|---|---|
| **Naive** | 4.25 / 5 | 20.5 / 25 (coherence 3.5/5) |
| **"Keep going until done"** | 4.5 / 5 | 24.0 / 25 (coherence 4.5/5) |
| **Causal-arc** | 4.5 / 5 | **24.5 / 25 (coherence 5.0/5)** |

- On **short tasks**: causal-arc ties with the simple imperative. Both produce complete deliverables; momentum is enough.
- On the **long task**: causal-arc wins decisively on design coherence — the dimension that matters most as decision count grows.
- **Naive cells exhibited concrete drift**: error-envelope models declared and never wired, two-shape 422 variants, status-code inconsistencies, stray artefacts in the repo, README claims unsupported by code.
- **Causal-arc was the only condition with perfect 5/5 coherence in both models** on the long task.

**Why this is an alignment result.** Behavioral alignment — telling the agent what to do — erodes under the training gradient that rewards check-ins, deference, and MVP-defaulting. Structural alignment — giving the agent a structural claim about the mandate — holds because the agent has integrated the principle, not memorised the rule. The benchmark demonstrates this concretely: on long unsupervised sequences where surface rules fail, structural framing actively maintains the coherence the simple imperative cannot.

The methodology aligns the agent with the *intention* of the mandate, not its surface form. That's the alignment claim, and it now has empirical support.

**Practical recommendation.** Use causal-arc for multi-file production builds, technical specifications propagating through code-docs-tests, long refactors, autonomous research arcs. For simple, well-specified tasks, simpler activations suffice. Cost: fifty tokens of prompt. Return: scales with task length and decision count.

**Open.** The library, methodology, eighteen benchmark cells, and the full judging audit trail (anonymised cells, blinded scoring, mapping disclosed only after scoring) are public.

---

*Read the methodology: [`methods/causal-arc-execution/`](methods/causal-arc-execution/) — structural argument, practice guide, anti-patterns, invocations, and full benchmark.*
