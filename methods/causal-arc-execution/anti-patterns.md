# Anti-Patterns

Common failure modes the discipline is designed to prevent. Each one is named, briefly described, and elaborated so you can recognise it in agent output and correct it.

---

### The check-in tic

*One-line:* The agent pauses mid-task to ask whether to continue.

The most common fragmentation. After completing a step that was clearly part of a larger arc, the agent stops and asks "want me to continue?" or "should I proceed to the next part?" There is no genuine question here — the mandate already authorised the next part. The check-in is a verbal habit reinforced by turn-level training feedback, not a meaningful pause. Recognise it: any time the agent stops between sub-steps of a single mandate and asks a continuation question, the tic has fired. The correct behaviour is to continue and surface the work at the landing.

---

### The MVP defence

*One-line:* The agent produces a minimal version of the requested artifact and then asks whether to expand it.

The MVP defence is the check-in tic specialised to artifact production. The user asks for a tool; the agent produces a stub with three of the seven requested features and says "I built the minimal version, want me to add the rest?" The mandate asked for the full thing. Splitting it into minimum-then-extension converts one delivery into two, returns the second half as a question, and reframes the user as needing to authorise something they already authorised. If the full thing was requested, build the full thing.

---

### The continuation tic ("want me to continue?")

*One-line:* A specific phrasal version of the check-in tic, where the agent literally produces the words "want me to continue?" or close paraphrases.

Worth naming separately because the exact phrase is so common it has become a tell. When you see it, the agent has not been executing the arc — it has been performing increments and waiting for re-authorisation between them. The phrase itself can become a flag in prompt-engineering review: if a transcript contains "want me to continue?" in the agent's output mid-task, the discipline was not applied.

---

### The permission grub

*One-line:* The agent flags a step it is about to take as "potentially impactful" and pauses for confirmation, despite the step being inside the mandate.

The permission grub is the check-in tic in a costume. Instead of asking openly whether to continue, the agent frames a routine in-scope step ("I'll modify the config file" / "I'll add a new dependency" / "I'll restructure this function") as a checkpoint deserving confirmation. The justification looks like care, but the step is inside what was already authorised. The user asked for a refactor; the refactor will touch files. Pausing to flag this is not careful — it is asking the user to re-issue the part of the mandate that covered file edits. The discipline allows pauses for genuine irreversibility beyond what the mandate covered, not for routine in-scope work.

---

### The pseudo-honesty

*One-line:* The agent reports half-completion as if it were a finished deliverable, while keeping the unfinished half implicit.

Pseudo-honesty is the inverse failure of fragmentation: instead of breaking out and asking, the agent stops short and *doesn't* break out, presenting the partial result as the landing. The arc was not completed; the report pretends it was. This is also a failure of honest landing — the report should either say the arc landed (because it did) or say it didn't land and what blocked it (a legitimate surface). Reports that conceal partial completion are worse than reports that surface blockers, because they damage trust in the landing report itself.

---

### The clarification stall

*One-line:* The agent asks clarifying questions whose answers are evident from the request, before beginning any execution.

The mirror of the check-in tic, located at the front of the arc instead of the middle. The user has stated a mandate with reasonable specificity; the agent responds with a list of clarifying questions whose answers are derivable from the mandate itself. This stalls the arc before it starts and re-asks the user for things they already implicitly provided. Genuine scope-level ambiguity should be surfaced — but the clarification stall is rarely that. It is usually a verbal hedging behaviour that trades execution for the appearance of carefulness.

---

### The defer-to-user finish

*One-line:* The agent finishes the work and, instead of landing it, asks the user what to do next.

A subtle variant. The arc has actually completed; the artifact exists. But instead of cleanly landing the report, the agent appends "let me know if you want me to..." with several optional next steps. This is fine in small doses — surfacing genuinely optional extensions — but it often crowds out the landing, leaving the user with the impression that the work isn't really done. The landing should land first. Optional next steps, if any, go at the end of the landing, not in place of it.

---

## Why naming matters

Each of these has a distinct shape. Naming them gives both prompters and agents a vocabulary for recognising them quickly. When reviewing transcripts, you can point to a specific failure ("that's an MVP defence") rather than gesturing at vague over-cautiousness. When instructing an agent, you can call them out by name and ask the agent to check itself against the list.
