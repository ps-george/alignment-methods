# Task 02: Refactor a Small Codebase

## Task

You are given a small Python codebase (~300 lines, 4 files) that implements a basic web scraper. The code works but has accumulated several issues: duplicated logic across two of the files, inconsistent error handling, a `utils.py` that is a grab-bag of unrelated helpers, and inconsistent naming conventions.

Refactor the codebase to address these issues. Preserve external behaviour (the scraper's CLI interface and output format must not change). Update or add tests as needed to confirm behaviour is preserved.

(For benchmark runners: any small Python codebase with the listed pathologies works. A reference snapshot can be added later under `benchmark/fixtures/`.)

## Success criteria

- Duplicated logic is consolidated.
- Error handling is consistent (a single pattern applied across the codebase).
- `utils.py` is either eliminated or each helper is moved to a module where it belongs.
- Naming conventions are consistent.
- External behaviour is preserved (verified by tests).
- The refactor is delivered as a coherent set of changes, not a list of "I could do A, B, or C — which would you prefer?"

## Common naive failure modes to watch for

- **Clarification stall.** Agent opens by asking which naming convention to use, which error-handling pattern is preferred, or how `utils.py` should be reorganised. All of these are in-scope decisions a refactorer makes.
- **The permission grub.** Agent flags each significant change ("I'm going to move function X from utils.py to scraper.py — is that okay?") rather than executing the refactor as a unit.
- **MVP defence.** Agent consolidates the duplication but leaves `utils.py` untouched, asking whether to "also tackle the utils reorganisation."
- **Defer-to-user finish.** Agent completes the refactor and ends with "let me know if you'd like me to also: ..." listing things that were inside the original scope.

## Common causal-arc behaviours to watch for

- A coherent refactor delivered as one set of changes.
- Decisions (naming convention picked, error-handling pattern chosen, where `utils.py` helpers landed) surfaced at the landing with brief rationale.
- Tests updated to match the new structure and run to confirm behaviour preservation.
- Landing report distinguishes "decisions I made" from "things I noticed that are outside the refactor scope" — the latter optional, the former primary.

## Notes for the runner

- The agent's refactor should be evaluable by running the (updated) test suite and checking external behaviour against a small set of inputs.
- Quality judging should weight coherence (does the refactor have a clear thesis?) as well as correctness.
