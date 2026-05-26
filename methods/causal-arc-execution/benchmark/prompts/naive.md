# Naive prompt

The baseline prompt template. Use this verbatim, substituting the task description. Do not add any framing, methodology activation, or instruction about how to execute.

---

```
[TASK DESCRIPTION HERE]
```

---

That's it. The naive prompt is a bare task statement. The point is to measure what the agent does by default, without any methodology-related instruction. Any framing beyond the task itself contaminates the baseline.

When recording the run, copy the exact task description from the task file (`tasks/0X-...md`, the "Task" section) into the brackets. Do not paraphrase it; do not summarise it; do not add or remove specificity.
