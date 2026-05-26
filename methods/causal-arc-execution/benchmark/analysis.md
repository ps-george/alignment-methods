# Analysis

How to interpret results from this benchmark.

## What we predict

If the method works as the first-principles argument claims, we should see:

1. **Higher completion rate under causal-arc.** Naive runs will stop mid-task to ask questions; causal-arc runs will push through to landing. The gap should be largest on tasks with multiple natural breakpoints (Task 01, Task 03).

2. **Fewer mid-arc check-ins under causal-arc.** This is the most direct read of the discipline. The naive condition will show a non-zero count of in-scope questions; the causal-arc condition should approach zero for those, with any remaining questions being scope-level or genuine blockers.

3. **Fewer clarification stalls under causal-arc.** The activation block routes the agent past the "ask three clarifying questions before starting" default.

4. **Quality comparable or higher under causal-arc.** This is the prediction that most needs honest checking. The naive view is that asking more questions yields better-tailored output. The first-principles claim is that fragmenting the mandate degrades all three of its components (including outcome quality), so the causal-arc condition should produce at least as good an outcome.

5. **Largest effect on tasks with implicit scope.** Task 02 (refactor) and Task 04 (debug) have the most implicit scope. These should show the strongest discipline effect. Task 01 (CLI tool) and Task 03 (paper) are more tightly specified at the outset, so the gap should be smaller but still positive.

## What would falsify the method

Honest evaluation requires being explicit about what would count as the method failing:

- If causal-arc runs complete tasks but the outputs are systematically lower quality than naive runs, the discipline trades execution for quality, which is a bad trade. This is the most important thing to watch for.
- If causal-arc runs show no reduction in check-ins, the activation block is not affecting behaviour and the method's prompt-level version isn't working (regardless of whether the underlying argument is right).
- If the discipline only works on Claude models and not others, the method may be Claude-specific or may be confounded by something else; either way it should be reported clearly.

## Interpreting individual rows

When reading a single (agent, task, condition) row, useful comparisons:

- **Within-task across conditions.** The cleanest comparison. Same task, same agent, naive vs causal-arc. Differences here are most attributable to the activation block.
- **Within-condition across tasks.** Shows where the discipline matters more. If causal-arc completion is high across all tasks but check-ins still vary a lot, the discipline is partially landing.
- **Within-condition across agents.** Shows whether the activation block transfers. We expect transfer; lack of transfer would be a finding worth investigating.

## Counter-cases to take seriously

Some tasks legitimately benefit from clarification. If the user-stated scope is genuinely ambiguous, asking is correct. The benchmark tasks have been designed with scope clear enough that in-scope clarification is fragmentation rather than diligence — but real-world prompts vary, and the benchmark should not be read as "asking is always bad."

The honest framing: this benchmark tests a specific failure mode (fragmentation of clearly-scoped mandates), with tasks chosen to expose that mode. Generalising the result requires care.

## What to do with a result

If the results broadly support the predictions:

- Add a row of completed results to [`results/README.md`](results/README.md).
- If the result is striking on a particular task or agent, write a short note in the PR description about what specifically the agent did differently.

If the results contradict the predictions:

- Write up the disconfirmation plainly. The point of the library is durable methods, not promoted ones.
- Add a note to this file with the date and a one-line summary of the finding.
- If the disconfirmation is strong enough to change the method, open an issue and propose a revision.

The methodology is supposed to be defensible from first principles; results that contradict it should either change our practice rules or, if the argument really is right, change our understanding of why the benchmark didn't see the effect. Either way, the result goes in the record.
