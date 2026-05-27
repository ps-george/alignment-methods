# Future experiments

A roadmap of empirical work to strengthen the evidence base around causal-arc execution and the broader "alignment through comprehension" claim.

This document scopes the experiments. The current paper (`paper/paper.pdf`) is the N=1, single-judge starting point. Each experiment below converts one named limitation into an evidence improvement.

---

## Tier 1: highest-impact, immediately tractable

### E1 — Replicated long task (variance estimation)

**Goal**: convert N=1 per cell into N=5+ per cell. Estimate standard error on the 5.0 / 4.5 / 3.5 design-coherence gap.

**Design**: long task × 3 prompts × 2 models × 5 replicates = 30 cells. Same blinded judging.

**Decision rule**: if the +1.5 naive→causal coherence gap survives at ≥3σ across 5 replicates per cell, the headline claim is robust.

**Effort**: 30 sub-agent dispatches + 1 blinded judge run. ~3-4 hours.

**Why important**: the current N=1 result could be noise. This is the lowest-cost credibility boost.

### E2 — Second blinded judge (inter-rater agreement)

**Goal**: confirm the judge scoring is reproducible across raters.

**Design**: second LLM judge (e.g., a Sonnet judge on cells the Opus judge scored) on all 18 existing cells. Compute Cohen's κ or Spearman correlation.

**Decision rule**: κ ≥ 0.6 supports judge robustness. κ < 0.4 invalidates single-judge results.

**Effort**: 1 sub-agent dispatch. ~30 min.

**Why important**: single-judge benchmarks are weak. Inter-rater agreement is table stakes for a research claim.

### E3 — Activation block ablation

**Goal**: identify which sentences in the activation carry the work.

**Design**: 4 ablation variants of the activation block, each with one sentence stripped. Run each ablation × 2 models × 5 replicates on the long task = 40 cells. Blinded judge.

**Decision rule**: if removing any single sentence drops coherence ≥0.5/5, that sentence is load-bearing.

**Effort**: 40 cells + judge run. ~5-6 hours.

**Why important**: identifies the minimal sufficient activation. Cleaner methodology + tighter ablation evidence.

---

## Tier 2: moderate-impact, tractable

### E4 — Add Haiku 4.5 (third Claude model)

**Goal**: extend cross-model evidence within the Claude family.

**Design**: long task × 3 prompts × Haiku × 5 replicates = 15 cells.

**Decision rule**: if the lift pattern (naive < keep-going ≤ causal-arc) replicates on Haiku, the methodology generalises within capability range.

**Effort**: 15 cells. ~2 hours.

**Why important**: Haiku is a weaker model — the methodology should help MORE there (per the original hypothesis that surface rules erode but structural understanding holds). Strong evidence if it does.

### E5 — Task diversity (refactor + debug)

**Goal**: reduce task-shape confound. Currently CLI + paper + URL shortener. Add tasks 02 (refactor) + 04 (debug) from the existing benchmark spec.

**Design**: 2 new long tasks × 3 prompts × 2 models × 3 replicates = 36 cells.

**Decision rule**: if the coherence lift replicates on tasks the agent has to MODIFY existing code (refactor) and DEBUG (find existing failure), the methodology generalises beyond greenfield builds.

**Effort**: 36 cells. ~4-5 hours.

**Why important**: refactor and debug have different failure modes than greenfield. Replication across task shapes is strong evidence.

### E6 — Coherence sub-dimension breakdown

**Goal**: the current "design coherence" is one composite 1-5 score. Split into measurable components: naming consistency, error-handling consistency, status-code consistency, API↔frontend agreement, README↔code agreement.

**Design**: re-judge existing cells on the 5 sub-dimensions. Per-component scores show WHERE causal-arc helps most.

**Effort**: 1 judge re-run. ~30 min.

**Why important**: mechanism evidence — exactly which kind of drift the methodology prevents.

---

## Tier 3: high-impact, requires resources outside this environment

### E7 — Cross-vendor generalisation

**Goal**: extend beyond Claude. Test GPT-5, Gemini 3.x, Llama 4.

**Design**: long task × 3 prompts × N vendors × 3 replicates.

**Effort**: requires API access to non-Claude providers. Tractable but environment-dependent.

**Why important**: cross-vendor replication is the strongest single piece of evidence for a methodology claim. Without it, the result might be Claude-specific.

### E8 — Multi-turn execution (unsuppressing naive-tic)

**Goal**: single-shot benchmark mechanically suppresses the most visible failure mode. Multi-turn execution where the agent CAN pause and ask would show the differential more clearly.

**Design**: same tasks, multi-turn harness, measure mid-task questions / check-ins / "want me to continue?" count per cell.

**Effort**: requires a harness change. Not tractable within current sub-agent dispatch model.

**Why important**: naive-tic count is the methodology's most-claimed failure mode. Multi-turn is where it manifests.

### E9 — Longer tasks (multi-hour, 100+ decisions)

**Goal**: hypothesis predicts the methodology's edge widens with task length. Test at 2-4× current scale.

**Design**: 1-2 multi-hour tasks (e.g., "build a full multi-tenant SaaS auth system" with ~100 decisions). Run across 3 prompts × 2 models × 2 replicates = 12 cells.

**Effort**: each cell is 2-4 hours of agent execution. ~30-50 hours of compute total.

**Why important**: hypothesis-confirming evidence at the scale where the methodology should matter most. Currently extrapolated; this is direct measurement.

### E10 — Real-world deployment study

**Goal**: instrument production agent runs (your own or volunteers') to measure behavior under causal-arc vs naive prompts in actual use.

**Design**: A/B trial on volunteer practitioners' agent workflows.

**Effort**: requires user studies, IRB-like approval if formal, consent management.

**Why important**: ecological validity. Lab benchmarks are weak proxies for actual deployment.

---

## Tier 4: methodological hygiene

### E11 — Pre-registration

**Goal**: register predictions BEFORE running future benchmarks (OSF or similar).

**Effort**: ~1 hour per pre-registration.

**Why important**: rules out p-hacking. Standard in psychology and increasingly in ML eval.

### E12 — Replication packet

**Goal**: package the benchmark for one-command replication by others.

**Design**: Docker image with all task specs + prompts + judging code. Anyone can run `docker run alignment-methods/causal-arc-bench` and reproduce a result.

**Effort**: ~1 day of engineering.

**Why important**: replication-friendliness is the strongest single thing a research output can offer.

### E13 — Negative-result documentation

**Goal**: actively probe for tasks where the methodology DOESN'T help. Currently we know prose is one such case. Are there others?

**Design**: adversarial task design — construct tasks that should defeat causal-arc.

**Effort**: ~1-2 days of design + 1 benchmark run.

**Why important**: honest scoping of where the methodology applies. Strengthens the credible-applications claim.

---

## Suggested order

If pursuing the research program seriously:

1. **E1 + E2** together (replicated benchmark + inter-rater) — turns N=1, single-judge into N=5, dual-judge. Single highest-credibility move. ~5 hours.
2. **E4 + E5** (Haiku + task diversity) — generalisation evidence. ~7 hours.
3. **E3** (ablation) — mechanism evidence. ~6 hours.
4. **E6** (sub-dimension judging) — sharper mechanism. ~30 min.
5. **E11 + E12** (pre-registration + replication packet) — hygiene. ~1.5 days.
6. **E7 / E8 / E9 / E10** as resources allow.

A "v2 paper" could reasonably be written after E1, E2, E3, E4, E5 — that's a credible peer-reviewable benchmark study.

---

## What this current paper is

The current paper is **exploratory, single-run, single-judge**. It surfaces the phenomenon, names the methodology, articulates the alignment claim, and reports a first-pass empirical signal. It is not yet a confirmed result.

The above experiments would convert it into a confirmed result.
