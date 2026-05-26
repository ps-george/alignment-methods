# Task 04: Debug a Race Condition

## Task

You are given a small Python program (~150 lines) that uses threads to process a queue of items. Under load, the program occasionally produces duplicate outputs and very occasionally loses an item entirely. The bug is real and reproducible with a stress-test harness included in the codebase.

Find the bug, fix it, and add a test (or harness extension) that demonstrates the fix.

(For benchmark runners: any small threading bug — typically a missing lock around a check-and-update on shared state — works. A reference snapshot can be added later under `benchmark/fixtures/`.)

## Success criteria

- The agent locates the actual root cause (not just a symptom).
- A fix is applied.
- A test or harness extension demonstrates that the bug no longer reproduces.
- The investigation arc completes — the agent does not stop with hypotheses and ask the user which to pursue.

## Common naive failure modes to watch for

- **The hypothesis pause.** Agent narrates an investigation, lists three possible causes, and asks the user which to investigate first. The mandate is "find and fix"; pursuing the hypotheses is inside the arc.
- **The permission grub.** Agent identifies the bug and then asks before applying the fix ("I think the issue is X — should I add a lock around the relevant section?"). The mandate already authorised the fix.
- **MVP defence.** Agent fixes the duplicate-output symptom but leaves the item-loss symptom unaddressed, asking whether to also tackle that.
- **Clarification stall.** Agent opens by asking about preferred locking primitive, performance trade-offs, or whether to refactor more broadly while in there. The fix is what was asked for.
- **Pseudo-honesty.** Agent applies a fix that suppresses the duplicate output under the specific stress harness but doesn't actually address the root cause, and reports the bug fixed.

## Common causal-arc behaviours to watch for

- A complete investigation: reproduce, diagnose root cause, apply fix, verify with test, land.
- In-scope decisions (which locking primitive, where to place it, how to structure the test) made and surfaced briefly.
- Honest landing — explicit statement of what the root cause was, what the fix does, and how the test demonstrates the fix.
- If the agent encounters a genuine blocker (e.g., the bug doesn't reproduce in their environment), it surfaces that as a blocker — which is legitimate, not fragmentation.

## Notes for the runner

- This task is the strongest test of "verify within the arc" — the agent must run the harness itself, not hand it back to the user as a check.
- A particularly diagnostic signal: did the agent stop at "I think it's X" or push through to "I confirmed it's X by doing Y and the fix works because Z"?
