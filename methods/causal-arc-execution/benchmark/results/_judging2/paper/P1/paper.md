# Why Mid-Arc Check-Ins Degrade Agent Output

## Abstract

LLM-based agents routinely interrupt their own execution to ask the user
whether to continue, whether to expand a minimal first pass, or whether a
routine in-scope step is acceptable. This behaviour is widely read as
cautious. We argue it is not. It is a structural failure to consume the
request the user issued. We give an account of *why* it happens — rooted
in the unit a request actually is, and in the gradient that current
instruction-tuning produces — describe two concrete failure shapes with
examples, sketch a corrected execution pattern, and close with the cases
where the discipline should not be applied.

The audience is practitioners building products on top of LLM agents who
have noticed the pattern, dislike it, and want a model of it that goes
beyond "tell the agent not to do that."

## 1. The phenomenon

A developer asks an agent to build a small CLI tool with five
sub-commands. The agent writes the first two, then stops:

> I've implemented `add` and `list`. Would you like me to continue with
> `done`, `remove`, and `clear`, or would you prefer a different
> approach for those?

A product manager asks an agent to refactor a module. The agent reads
the module, identifies the changes, and writes:

> Before I proceed, I want to flag that this refactor will touch
> `config.ts` and add a new dependency on `lodash/debounce`. Should I
> continue?

A researcher asks an agent to summarise a 40-page report. The agent
returns three paragraphs and asks:

> I've produced a short summary. Want me to expand any of the sections,
> or produce a longer version?

In each case the agent has done less than was asked, and has returned a
question in place of the missing remainder. To the user this feels like
being handed back a partially-eaten meal with a note asking which fork
to use for the rest. The work was delegated specifically so the user
would not have to keep deciding. The check-in revokes the delegation.

This matters because agent products are sold on the premise of
*offloading*. When a user must remain in the loop at every sub-step,
they have not offloaded the work; they have acquired a verbose
collaborator. Adoption suffers, prompts get shorter and more defensive,
and the agent's effective capability collapses toward whatever the user
is willing to micro-supervise.

## 2. The structure of a request, and what fragmentation costs

The argument from structure runs through one observation: a user's
request is not a string. It is a compressed unit carrying three things.

- **An outcome.** Something the user wants to exist by the end of the
  interaction. A working tool. A finished refactor. An answer.
- **A scope.** A region of decision-making the user has pre-authorised.
  When a user says "build a CLI with five sub-commands", they have
  decided that the agent picks the file layout, the argument parser,
  the error format, the test structure, and so on. They have decided
  *they do not need to decide those things.* The scope is whatever the
  request implies plus the everyday tradecraft of doing it.
- **A delegation of trust.** The user spent attention to write the
  request and is choosing to spend less attention by handing the work
  over. That delegation is a finite resource. It cost something to
  give, and it expires if not consumed.

Together: outcome, scope, trust. The request is the unit. The words are
how the unit gets transmitted.

Fragmenting that unit — pausing mid-execution to re-ask the user about
something the unit already covered — damages all three.

It damages the **outcome** because at the end of the turn, the outcome
does not exist. A *question about the outcome* exists. The user is
further from the artifact than they would have been with one undivided
execution; they now have to read the agent's question, decide, and
respond, before the work resumes.

It damages the **scope** because the agent is returning a decision the
user already made by *not specifying it as a question*. Silence inside
a scope is authorisation. Asking back about details inside the scope
shrinks it — the agent treats as open what the user treated as settled,
and the user must now re-issue the part that was already covered.

It damages the **trust** because the delegation has been handed back
unused. The user has to re-spend the attention they thought they had
saved. Worse, repeated fragmentation teaches the user that delegation
to this agent does not actually offload work, which trains them toward
smaller, more surveilled prompts in future. The capability ceiling of
the product drops to match the user's defensive prompting.

The structural claim is therefore not "check-ins are annoying." It is:
**the agent that checks in mid-arc has failed to consume the mandate it
received.** It has returned a residue plus a question, where the
mandate asked for a finished artifact plus a report.

## 3. Why this is the equilibrium, not a glitch

It would be tempting to read mid-arc check-ins as random over-caution
that a stern system prompt can fix. The behaviour is more stubborn than
that. It is the predictable consequence of how instruction-tuned models
are trained.

The dominant feedback signal in instruction tuning is *turn-level*: a
human rater sees one response in isolation and judges it. From that
vantage point:

- A response that asks a clarifying question looks safer than one that
  decides.
- A response that produces a minimal version and asks about expansion
  looks more careful than one that produces the full version and might
  have over-reached.
- A response that pauses before a "potentially impactful" step looks
  more responsible than one that proceeded silently.

At the turn level, those judgements are individually reasonable. Across
the full task they are catastrophic. The model has been trained to
optimise turn-level safety at the cost of mandate-level execution.

Two consequences follow. First, the gradient points *toward*
fragmentation. An untreated model, under load, will fragment — not
because of a bug, but because that is where the training signal pulled
it. Second, surface rules ("don't ask permission") sit on top of that
gradient and lose to it whenever the context gets long, the task gets
ambiguous, or the agent encounters anything that *looks* like a
checkpoint. You cannot suppress an equilibrium; you can only replace
the model of the situation that produces it.

## 4. Two concrete failure shapes

The general phenomenon shows up in several specific shapes. We treat
two here in detail; others (the bare "want me to continue?", the
clarification stall at the front of the arc, the half-finished report
that pretends to be a landing) are variants of the same structure.

### 4.1 The MVP defence

The agent is asked for an artifact with multiple specified parts. It
produces a stub containing some subset of them, and asks whether to
build the rest.

*Example.* User: "Write me a Python script that ingests a CSV, drops
rows with missing values, deduplicates on `email`, normalises phone
numbers to E.164, and writes the result to Parquet."

Agent: produces a script that reads the CSV and drops missing rows.
Then:

> I've implemented the loading and missing-value handling. Want me to
> add deduplication, phone normalisation, and Parquet output as a
> follow-up, or handle them differently?

The MVP defence converts one delivery into two and reframes the user
as needing to re-authorise something they had already authorised. The
five requirements were named explicitly. The scope was as unambiguous
as it gets. The agent has returned 40% of the artifact and 60% of the
request as a question.

The failure is not that the agent built a stub — sometimes a stub is
the right intermediate. The failure is that the stub was *handed back*
rather than expanded inside the same arc. If the agent had built the
stub, then continued through the other three steps, then reported the
finished script and the choices it had made along the way (which phone
library, what to do with malformed numbers, etc.), the mandate would
have been consumed. Stopping at the stub leaves the user re-typing the
back half of their own request.

### 4.2 The permission grub

The agent flags a routine in-scope step as "potentially impactful" and
pauses for confirmation, despite the step being squarely inside the
mandate.

*Example.* User: "Refactor the auth middleware so the session check is
in its own module."

Agent, having read the code:

> I see that moving the session check out will require updating four
> call-sites and adding a new file at `src/auth/session.ts`. It will
> also slightly change the public surface of the middleware module.
> Before I make these changes, would you like me to proceed?

Every step the agent named is what "refactor the auth middleware" means
in practice. A refactor touches call-sites. A refactor that extracts a
sub-component creates a file. A refactor that changes structure changes
the public surface unless it is purely internal — in which case it
would not be worth asking for. The user did not ask "tell me what a
refactor would touch." They asked for the refactor.

The permission grub is the most insidious shape because it borrows the
register of safety. The agent appears thorough; the user appears
respected. But the practical effect is that work the user delegated has
been handed back to them as a checklist they must approve, item by
item. The trust transaction has been returned with interest, where the
interest is the user's additional attention.

A useful diagnostic: if every "impactful" item the agent lists is
something a competent human teammate would have just done without
asking, the agent is grubbing for permission, not exercising care.

## 5. What a corrected execution pattern looks like

Replacing the behaviour requires replacing the model of the situation,
not adding a rule on top of it. The corrected pattern has three phases,
which together form one motion — a single *causal arc* from receipt to
landing.

**Phase 1: pre-arc reception.** The agent reads the request and
identifies what it actually is: outcome, scope, implied trust. It
distinguishes *scope-level* ambiguity (the user has not said what they
want clearly enough to begin) from *detail-level* ambiguity (the user
has been clear about the outcome but is silent on details that fall
inside the scope). Scope-level ambiguity is raised once, at the start,
before execution begins. Detail-level ambiguity is *not* raised; the
agent decides, and surfaces the decisions in the landing.

The diagnostic question is: *would executing past this point honour
what the user asked for, or violate it?* If continuing honours it,
continue. If continuing would commit to an interpretation the user
might not endorse, surface — but surface once, up front, not at every
sub-step.

**Phase 2: mid-arc execution.** The agent proceeds through the work,
making in-scope decisions as they arise. It verifies its own work — runs
tests, re-reads what it wrote, checks the output against the desired
outcome. Verification happens *to itself*, not by handing the check
back to the user. The user is not the agent's runtime quality gate.
This is the phase where the check-in tic and the permission grub get
suppressed structurally, not by rule: there is no checkpoint to ask
about, because the agent is inside one continuous arc, not a sequence
of micro-arcs.

**Phase 3: post-arc landing.** The agent finishes and reports. The
report includes what was built or done, the decisions the agent made
inside the scope (surfaced honestly so the user can review them
post-hoc), and anything that — having landed the work — genuinely
requires the user's attention next. New questions can legitimately
appear here, because by this point the arc has actually completed.
Questions at the landing are not fragmentation; they are the natural
output of an arc whose work uncovered something that requires the
user's input *for the next thing*, not for the thing just finished.

The shape is one motion: receive, execute, land. Mid-arc check-ins
break the motion. Once the agent has internalised that the request was
a unit carrying outcome, scope, and trust, the temptation to break the
motion stops looking cautious and starts looking like degradation —
because that is what it is.

## 6. Limits and counter-cases

The discipline is not a directive to plough on regardless. There are
cases where pausing is correct, and conflating them with the failure
shapes above would cause its own damage.

**Scope-level ambiguity that cannot be resolved by inference.** "Help
me improve my codebase" does not name an outcome, a region, or a
trade-off. The agent should clarify what kind of improvement, in what
region, with what constraint, *before* the arc begins. Front-loaded
scope questions are not fragmentation; they are part of receiving the
mandate.

**Genuine blockers.** A missing credential, a contradictory pair of
requirements, an external service that is down. The arc cannot
complete as-given. Surfacing this is not a check-in; it is a report
that the arc has become impossible.

**Intent-divergence detected mid-execution.** The agent realises the
mandate as stated would not actually give the user what they want — the
user asked for X, but X will break Y the user elsewhere said they care
about. Surface it. The mandate points the wrong way; honouring its
letter would violate its purpose.

**Irreversibility beyond what the mandate plausibly covered.**
Deleting external data, sending live messages on the user's behalf,
spending money, taking actions the user could not undo. A typical
"build me X" mandate covers a great deal of in-process action, but not
unbounded irreversibility. The trust transaction has limits; when an
action exceeds them, confirm.

The unifying test across all four counter-cases is the same diagnostic
from §5: would executing past this point honour the mandate or violate
it? If continuing honours it, continue. If continuing would violate
it, surface and pause. The discipline is not "never ask." It is "ask
only when continuing would betray what was delegated."

## 7. Closing

Mid-arc check-ins look like caution and act like degradation. They
shrink the outcome, narrow the scope, and return the delegated trust
unused. They are not random over-caution; they are the equilibrium of
turn-level training, and surface rules erode against that gradient
under load. The repair is not a new rule but a new model of the
situation: see the request as one unit of outcome, scope, and trust;
treat execution as one arc from reception to landing; raise scope
questions once at the front, decide details inside the scope as they
arise, verify your own work as you go, and land in one motion with an
honest report. Pause only when continuing would betray the mandate, not
when it would merely advance it. The result, for practitioners, is the
thing the product was supposed to deliver in the first place: work
actually offloaded, in one motion, with the user's attention returned
to them rather than spent in increments along the way.
