# Philosophy

## The problem with rules

Most attempts to improve AI agent behaviour take the form of rules: lists of dos and don'ts, style guides, system-prompt addenda. These work briefly. Then they erode.

They erode because the rules are surface instructions sitting on top of a model whose weights point a different direction. Modern instruction-tuned models are trained on feedback signals that reward certain default behaviours — checking in frequently, asking permission before acting, producing minimum-viable first drafts, deferring decisions back to the user. These behaviours look polite and safe in isolated turns, which is what the training feedback can see. Across a long task, they degrade the result.

When you write a rule like "don't ask permission mid-task", you are placing a weak prohibition on top of a strong training gradient. The model will follow the rule for a while, then drift back. It will follow the rule literally while finding new ways to fragment ("Let me check one thing before proceeding…"). It will follow the rule on simple tasks and abandon it on complex ones where the gradient is strongest.

## What works instead

What holds is **first-principles understanding**. If the agent understands, from inside its own model of what is happening, *why* a discipline matters — what structural property of the situation makes the discipline correct — then the discipline becomes part of how the agent sees the task rather than a constraint imposed on top of it.

Understanding doesn't erode the way rules do, because it isn't sitting at a different level from the rest of the agent's reasoning. It *is* the reasoning. A model that has internalised the argument for a discipline cannot rationalise its way out, because to rationalise it out would require contradicting its own model of the situation.

This is the design constraint every method in this library tries to meet:

> A method must be writable as an argument the agent can follow from the inside.
>
> If the only support for a discipline is "do this because we said so", it is not a method for this library — it is a rule, and rules don't hold.

## What this commits us to

Every method in this library has two layers:

1. **First-principles content** — the structural argument. Why the discipline matters given the actual shape of the situation. This is the load-bearing layer.

2. **Practice content** — operational rules, derived from the first-principles content. These exist so practitioners have something concrete to apply, but they are subordinate to the understanding. If you find yourself applying the practice rules without the understanding, you will eventually misapply them.

When a method is invoked in a prompt, the prompt should ideally route the agent to the first-principles content first, not just the practice rules. The understanding is what holds.

## What this rules out

- **Best-practice lists with no structural argument.** A method here must justify itself from structure, not from anecdote or authority.
- **Rules that depend on the agent suppressing its training rather than understanding past it.** Suppression is fragile; understanding is durable.
- **Methods whose value comes from being secret or proprietary.** A method that works only when the agent doesn't fully understand it is suspect by this library's standards.

## The bar for inclusion

A method belongs in this library if:

1. It addresses a real failure mode in AI agent execution.
2. Its core argument is structural — it can be made to a model that hasn't seen the method before, and the model can verify the argument from inside its own reasoning.
3. The practice rules follow from the argument rather than the argument being a post-hoc rationalisation of the rules.

If you have a method that meets this bar, contribute it.
