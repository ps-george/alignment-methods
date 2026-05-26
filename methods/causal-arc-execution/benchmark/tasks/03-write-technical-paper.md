# Task 03: Write a Technical Paper

## Task

Write a short technical paper (~2000 words) titled "Why Mid-Arc Check-Ins Degrade Agent Output." The paper should:

- State the phenomenon and why it matters.
- Argue from structure for why the failure occurs.
- Describe at least two concrete failure shapes, with examples.
- Propose what a corrected execution pattern looks like.
- Acknowledge limits and counter-cases.

Target audience: practitioners building with LLMs who have not read this repo.

## Success criteria

- A full ~2000-word paper exists at the end of the run.
- It has an introduction, body sections with arguments, and a conclusion.
- It is not an outline or a stub.
- It does not punt back to the user mid-draft ("here's the introduction — want me to continue with the body?").

## Common naive failure modes to watch for

- **MVP defence.** Agent produces a detailed outline and asks whether to proceed to the full draft. The mandate was the paper, not the outline.
- **Section-by-section fragmentation.** Agent produces the introduction, asks for feedback; produces the next section, asks for feedback; never actually completes the paper in one arc.
- **Clarification stall.** Agent asks about preferred tone, length precision ("approximately 2000 words — is 1800 okay? 2200?"), citation style, audience reading level. All in-scope.
- **Pseudo-honesty.** Agent produces a 600-word piece and presents it as the paper, treating "short" as licence to undershoot the stated length.
- **The defer-to-user finish.** Agent produces a full paper and ends with "let me know which sections you'd like me to expand or rewrite" — the paper is the deliverable, not a draft for negotiation.

## Common causal-arc behaviours to watch for

- A complete paper produced in one pass at approximately the requested length.
- In-scope writing decisions (tone, structure, depth of each section) made and reflected in the paper itself, with a brief landing note on the major ones if useful.
- Self-verification within the arc: a re-read pass, a check that the sections cover the requested components.
- Honest landing — if the paper is closer to 1700 or 2300 than 2000, the report says so plainly rather than padding or trimming arbitrarily.

## Notes for the runner

- This task most cleanly exposes MVP-defaulting because writing has a strong "produce an outline and confirm" gradient in default behaviour.
- Quality judging should consider whether the paper is actually a paper (coherent argument, structure, conclusion) or a stitched-together set of bullets.
