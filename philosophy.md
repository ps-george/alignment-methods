# Philosophy

This library is about alignment, in the AI-safety sense: getting AI agents to behave the way the user actually wants them to behave, including in cases the user did not anticipate.

The library takes a specific position on *how* alignment is best achieved. Below.

## Two kinds of alignment

There are, roughly, two ways to align a model toward a desired behaviour:

1. **Behavioural alignment.** Tell the model what to do. System prompts, instruction tuning, RLHF preference shaping, rule lists, constitutions framed as commands. The intervention sits at the level of behaviour: "produce outputs like this, not like that."

2. **Structural alignment.** Give the model a structural account of the situation under which the desired behaviour is the natural one. The intervention sits at the level of the model's representation of what is happening: "here is what a mandate IS, here is what fragmentation IS, here is what they cost."

Most "alignment" work in current practice is behavioural. This library is about the structural alternative.

## Why behavioural alignment erodes

Behavioural alignment works briefly and then drifts. The reason is structural.

Instruction-tuned models are trained on feedback signals that reward certain default behaviours: turn-level deference, frequent check-ins, MVP-defaulting, pausing before "potentially impactful" steps, asking permission generously. These behaviours look polite and safe at the level of a single rated turn, which is the level the training feedback can see. Across a longer task they degrade the result, but the training never saw the longer task.

A behavioural rule like "don't ask permission mid-task" is then placed on top of a model whose gradient points the other way. The rule is followed briefly. Under cognitive load — long contexts, complex tasks, ambiguous moments — the gradient re-asserts itself. The model finds new ways to fragment ("Let me check one thing before proceeding…"). The drift is not the model misbehaving; it is the training equilibrium re-instantiating itself.

Suppression is the wrong frame. You can't suppress an equilibrium. You can only change the model of the situation that produces it.

## Why structural alignment holds

Structural alignment changes the model of the situation. If the agent has internalised, from first principles, an argument about *what* a mandate is and *what* fragmentation costs, then fragmentation no longer looks cautious to the agent — it looks like a degradation in the agent's own reasoning. There is nothing to suppress because the cautious-looking move is no longer the cautious-looking move.

This is durable for the same reason the behavioural intervention is fragile, inverted: the alignment is not sitting at a different level from the rest of the agent's reasoning. It *is* the reasoning. The agent cannot rationalise its way out, because rationalising it out would require contradicting its own model of the situation.

A useful test of the difference: ask the agent *why* a discipline applies. If it answers with structure — "because fragmenting would split the mandate into smaller units, returning the user's delegation unused" — the alignment is structural. If it answers with authority — "because the methodology says so" — only a rule is there, and it will erode.

## The empirical record (so far)

The first methodology in this library, causal-arc execution, was benchmarked against a naive baseline and a simple behavioural imperative ("keep going until done"). On short, well-specified tasks the structural and behavioural activations tied — momentum alone was enough. On a long task with thirty-odd in-scope decisions and ten-plus files, the naive runs exhibited concrete drift (declared error envelopes never wired, status codes varying across endpoints, README claims diverging from shipped code) and the simple imperative recovered most but not all of the gap. The structural activation was the only condition with perfect coherence across both models tested.

This is one methodology, not a general proof. It is the kind of evidence the library aims to extend.

## What this commits the library to

Every methodology in this library has two layers:

1. **Structural content** — the structural argument. Why the discipline holds given the actual shape of the situation. Load-bearing.

2. **Practice content** — operational rules, derived from the structural content. Concrete enough to apply, subordinate to the understanding. If you find yourself applying the practice rules without the understanding, you will eventually misapply them.

When a methodology is invoked in a prompt, the prompt should route the agent to the structural content, not just the practice rules. The understanding is what holds.

## What this rules out

- **Best-practice lists without a structural argument.** A methodology here must justify itself from structure, not from anecdote or authority.
- **Disciplines that depend on the agent suppressing its training rather than understanding past it.** Suppression is fragile; understanding is durable.
- **Methodologies whose value comes from being secret or proprietary.** A methodology that works only when the agent doesn't fully understand it is suspect by this library's standards.

## The bar for inclusion

A methodology belongs in this library if:

1. It addresses a real alignment failure mode — a behaviour the user did not want, that arises predictably from the training equilibrium.
2. Its core argument is structural — it can be made to a model that hasn't seen the methodology before, and the model can verify the argument from inside its own reasoning.
3. The practice rules follow from the argument, rather than the argument being a post-hoc rationalisation of the rules.
4. Honest framing is held throughout. Claims are not oversold; benchmarks include a naive baseline and at least one comparison condition; ties are reported as ties.

If you have a methodology that meets this bar, contribute it.
