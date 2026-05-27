# Invocations

Short phrases you can paste into a prompt to activate the causal-arc alignment methodology on a task. The phrases below are activation surfaces, not the methodology itself — they work by pointing the agent at the structural account, not by issuing a behavioural rule. Each phrase emphasises a slightly different facet; choose based on which failure mode you most expect from the agent on this task.

| Phrase | When to use |
|---|---|
| **"Execute as a single causal arc."** | General-purpose activation. Use as the default when you want the full discipline applied. Works well as a leading sentence before stating the task. |
| **"No MVP — full build."** | When you expect the agent to default to a minimum-viable version and then ask whether to expand. Forces it past the MVP trapdoor. |
| **"Don't pause for permission."** | When the task involves steps the agent might pre-emptively treat as "potentially impactful" — file edits, refactors, multi-file changes. Affirms the trust transaction up front. |
| **"Until completion."** | When the task has multiple natural breakpoints the agent might treat as good places to check in. Signals you want execution past them. |
| **"Build the whole thing."** | When the deliverable is a unified artifact (a tool, a paper, a system) and you want it landed as one piece, not delivered in fragments. |
| **"Decide and proceed where the scope is clear."** | When the task has many in-scope details you do not want to be asked about. Pairs well with longer task descriptions where you've front-loaded the scope. |
| **"Report at the landing, not at the steps."** | When you want to remind the agent that reporting comes at the end, not interleaved. Useful when prior interactions have trained it toward mid-arc updates. |

## Combining

For a strong activation, stack two or three. A solid default opener:

> Execute this as a single causal arc. Make decisions inside scope; don't pause for permission. Report at the landing.
>
> [task description]

For tasks where MVP-defaulting is the main risk:

> Build the whole thing. No MVP — full build, until completion. Decide and proceed where the scope is clear.
>
> [task description]

## A note on tone

These phrases work because they are direct, not because they are forceful. Stacking adverbs ("absolutely don't ask, never pause") does not increase the activation strength and can read as performance. One or two clean directives, then the task, is the strongest form.
