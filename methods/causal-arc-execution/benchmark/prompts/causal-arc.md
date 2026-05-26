# Causal-arc prompt

The methodology-activated prompt template. Use this verbatim, substituting the task description. The activation block is fixed across all tasks; only the task description varies between runs.

---

```
Execute this as a single causal arc.

A mandate is a complete unit of intention — outcome, scope, and a delegation of
trust. Fragmenting it into mid-arc check-ins degrades all three. Make
in-scope decisions as they arise rather than returning them. Verify your
work within the arc, not by handing the check back to me. Land the work in
one motion and report honestly at the end, including the substantive
decisions you made along the way. Save questions for things genuinely
outside the mandate's scope.

(Method reference: github.com/condri/agent-methods — methods/causal-arc-execution.)

Task:

[TASK DESCRIPTION HERE]
```

---

## Notes for the runner

- The activation block must be identical across the four tasks, so that any per-task variance in behaviour is attributable to the task and not to varied activation strength.
- The method-reference line is included to test whether agents that can resolve the reference make use of it. If the agent has no web access, it functions purely as context that the methodology is a deliberately structured discipline rather than ad-hoc instruction.
- As with the naive prompt, copy the task description verbatim from the task file. The activation block is the only difference between the two prompt conditions.
