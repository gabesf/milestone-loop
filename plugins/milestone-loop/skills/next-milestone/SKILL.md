---
name: next-milestone
description: Step 3 (the loop) of the milestone-loop workflow. Plans
  the next open milestone from docs/milestones.md, delegates the
  implementation to a subagent on a model chosen at plan approval,
  runs an adversarial review gate against the milestone's diff, executes
  every test step it can drive itself (browser, API, DB, stack tooling),
  then hands the user only the steps that genuinely need a human.
  Only makes a local, never-pushed checkpoint commit; the real commit is
  /close-milestone's job.
disable-model-invocation: true
---

# Implement the next milestone

Pick up the first open milestone, plan it, have a delegated implementer
build it under the quality gates, run the adversarial review gate, execute
every test step the harness can drive, and hand the user precise
instructions for only what it cannot. This skill makes ONE kind of commit:
a local `wip(M-XX)` checkpoint that is never pushed; `/close-milestone`
squashes it into the definitive commit after the user's green light.

Two rules run through every section:

- **This session orchestrates and judges; it does not write code.**
  Implementers write it (see "Delegated implementation"). Docs
  (milestones.md, handoff, testing doc, decisions) are always this
  session's own job.
- **Verify, don't trust.** Every green claim from a subagent — build,
  tests, a fix — is re-checked by this session running the project's full
  build and entire test suite itself. Green in a report is a claim; green
  in your own output is a fact. Red goes back to a fresh implementer with
  the failure output; it is not fixed here.

## Preflight

0. **Fresh-session check.** This skill must start a fresh session: this
   window has to last through planning, the gate, the user's testing
   feedback and `/close-milestone`. If the conversation already holds prior
   work (planning discussion, another milestone, anything beyond session
   boilerplate), stop and tell the user to `/clear` and invoke
   `/next-milestone` again. No "just this once".
1. `docs/milestones.md` must exist with at least one milestone. If not,
   stop and point the user to `/plan-milestones`. Then run the
   conventions' "Legacy check" (path as in step 6): tier and TDD tags are
   read from labels, so it goes before step 2. If a group handoff
   `docs/handoff/G-XX.md` exists, a parallel group is active: stop and
   point the user to `/next-group` (one active unit at a time,
   conventions "Parallel groups").
2. **Model-tier check (blocking, before any further reading).** Identify
   the target milestone (first `open` one, or the M-ID the user named) and
   its recommended tier, resolved to a model as the conventions' "Model
   tiers" section says. Read now only that section (path as in step 6) and
   CLAUDE.md's `Model …` lines; the rest waits for steps 5–6. If the
   session runs on a model below the tier's model, STOP: tell the user the
   tier and its model and ask them to switch with `/model`; continue only
   after they confirm. The plan must be produced by the recommended model,
   and analysis done by a weaker one first is wasted. No tier tagged: apply
   the same check against the model floor.
3. If the target milestone carries a `Group:` tag and its group could run
   now, say once that `/next-group` would run it with its partners;
   running it alone is the user's call. If a milestone is already
   `in-progress`, read `docs/handoff/M-XX.md`
   (if it exists) BEFORE asking anything, summarize it, and ask whether to
   resume (from its "Next step") or abandon. No handoff: ask the same,
   noting that resuming means re-reading the scope from scratch. On
   abandon: delete the handoff, reset the milestone to `open`, and revert
   any local `wip(M-XX)` commits (`git reset --soft` to unstage, then
   discard) — leave the tree clean.
4. If `git status` shows uncommitted changes, warn the user and ask how to
   proceed — a milestone starts clean so its diff is reviewable. A local
   `wip(M-XX)` for the milestone being resumed is fine; a `wip` for an
   already-closed milestone is not — flag it.
5. Read CLAUDE.md fully: it defines the build/test/tooling commands every
   gate below runs through.
6. Read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it. Load the stack reference as its "Stack reference"
   section says and apply its `next-milestone` sections — toolchain checks
   run NOW, before any implementation work.

## Plan

1. Read the target milestone — acceptance criteria, covered requirements,
   notes — and related decision records in docs/decisions/.
2. Present the plan. OPEN with a **two-line summary**: two
   plain-language sentences (no jargon) on what this milestone
   builds and what changes for the user. Then: what will be built, in what
   order, which files/assets are touched, how each acceptance criterion
   will be met, and the milestone's recommended tier if tagged (the user
   can still switch with `/model` before approving). CLOSE with
   the implementer-model question: "Implementer model? (default: X)" where
   X is the default implementer model from the conventions'
   "Model tiers" section. The answer is an alias or ID accepted by the
   Agent tool's `model` parameter (what an alias resolves to is the
   profile's business). Never accept one weaker than the model floor. An
   approval that doesn't mention the model means the default. Write
   nothing before approval.
3. Mark the milestone `in-progress` in docs/milestones.md.

## Delegated implementation

Implementers are plain `Agent` subagents (general purpose, `model` = the
alias chosen at approval). The split keeps the token-heavy loop on the
implementer's model and its noise (file reads, build logs) out of this context.
Do not undo that by reading implementation files "to keep up" — read a
file only to verify a specific claim or finding.

1. **Write the brief** into `docs/handoff/M-XX.md` (structure in
   "Handoff") — the same file the inter-session handoff uses, so a session
   that dies mid-implementation resumes through Preflight 3. "Done" is
   empty; "Remaining" is the approved plan in order with the files each
   step touches; "Decisions made" holds the plan's design decisions;
   "Implementer brief" holds what the implementer cannot infer: acceptance
   criteria verbatim, build/test commands from CLAUDE.md, the stack
   reference (passed as the conventions' "Loading references" section says
   for subagents), whether `TDD: yes` applies, and the scope rule. Commit
   nothing yet.
2. **Launch the implementer** — one per milestone by default. Prompt: read
   the handoff file, CLAUDE.md and the stack reference's quality-gates
   section FIRST; implement "Remaining" in order under "Quality gates"
   below; NEVER commit, stage, push, or touch docs/milestones.md; return a
   final report with exactly:
   - **Done**: what was built, with file paths.
   - **Gates**: the exact build/test commands run and their results.
   - **Self-report**: (a) what it claims works but did not verify (not
     built, not run, not exercised against real data/runtime); (b) what in
     this implementation will bite a future milestone. Each item names a
     file or behavior; "none" is valid, silence is not.
   - **Out of scope**: problems noticed but deliberately not fixed.
   - **BLOCKED** (instead of the above) when the brief doesn't settle a
     design decision: the question, the options, the working-tree state.
     A subagent cannot talk to the user, so it never guesses a design.
   Use several implementers only for independent parts (in parallel only
   on disjoint files) or when one returns partial work under context
   pressure; each later one gets the brief plus the updated "Done".
3. **On BLOCKED:** relay the question verbatim, record the answer under
   "Decisions made" (and in docs/decisions/ if it is a design change),
   then launch a fresh implementer from the current state.
4. **On return:** verify (the rule above), then update "Done"/"Remaining"
   and keep the Self-report — the gate and the testing doc use it.
5. **Fixes are delegated too.** Every later code change — gate fixes,
   fixes from the user's feedback — goes to an implementer on the same
   model with the finding list verbatim and the gate's minimal-fix rule.
   Only exception: one obvious edit in one file may be applied here.

## Quality gates (non-negotiable during implementation)

- After every significant batch of changes, build with the project's
  toolchain. Zero errors before proceeding.
- Run the existing tests and write cheap automated checks for new logic
  where the stack allows. Everything that CAN be verified mechanically
  (tests, build, scripts, CLI queries against the dev DB) MUST be — every
  mechanical check is a step removed from the user's manual script.
- **TDD when tagged.** If the milestone's Notes contain `TDD: yes`, each
  new engine behavior gets a failing test FIRST, then the code until it
  passes, then refactor. Tests exercise the contract (inputs, outputs,
  edge cases), not implementation details, and follow CLAUDE.md's test
  guidelines. Where a behavior has no programmatic assertion (e.g. visual
  only), document why in the testing doc and cover it manually.
- Respect CLAUDE.md's editing rules and the stack reference's
  `next-milestone / quality gates` section.
- Stay inside the milestone's scope. Something broken or needed outside it
  is noted for the user, never fixed silently.

## Adversarial review gate (automatic, before any handoff)

When implementation is verified green, run this gate before the user sees
anything — the user only tests code that survived it.

**Policy.** CLAUDE.md's `Review gate:` line (from `/plan-milestones`):
`all`, `tagged` (only milestones tagged `Adversarial gate: yes`), or
`none`. No line, or any other value = full gate. When the policy
skips this milestone, still make the checkpoint (step 1) and keep the
Self-report for the testing doc, then go to "Closing". The user chose
this trade-off at planning time: don't re-litigate it or sneak in
informal reviews.

1. **Checkpoint commit (local only):** `git add -A && git commit -m
   "wip(M-XX): pre-review checkpoint"`. NEVER push it. It
   freezes a green state (the rollback point) and its diff IS the review
   target. Merge the implementers' Self-reports, plus anything your own
   verification found, into one list for triage in step 4 — and do NOT
   pass it to the reviewers: their value is that they don't inherit the
   author's assumptions.
2. **Launch 3 reviewers in parallel** with the plugin's
   `adversarial-reviewer` agent on the standard tier's model (if
   unavailable, plain subagents on the same model). Each
   gets ONLY the diff (`git show HEAD -- . ':!docs/handoff'`), the
   acceptance criteria and CLAUDE.md — never this session's reasoning,
   which the handoff file holds — and is told to ATTACK the change and
   not to open `docs/handoff/`. One lens each:
   - **Bugs & correctness**: broken edge cases, violated invariants from
     the systems docs, regressions of earlier milestones' behavior, skipped
     error paths, swallowed exceptions, silent fallbacks that mask
     failures.
   - **Overengineering & leftovers**: generality beyond the criteria, dead
     code, debug leftovers, TODOs, hard-coded values CLAUDE.md says must be
     configurable, and duplication — searching the EXISTING codebase for
     logic the diff reimplements.
   - **Scope & project-rule compliance**: scope creep, violations of
     CLAUDE.md rules and decision records.
   Each returns findings with file:line, severity and 0–100 confidence.
3. **Filter:** drop findings below 80 confidence, pre-existing issues,
   nitpicks, and anything a linter/compiler catches. Exception to the
   confidence cut only: a finding below 80 that names the same problem as
   a Self-report item survives — two independent sources outweigh one
   reviewer's doubt.
4. **Triage** the survivors together with the Self-report list:
   - flagged by both sides → strong confirmation, fix first;
   - real and in scope → fix; real but out of scope → the relevant
     milestone's Notes; wrong → dismiss with a one-line reason;
   - Self-report items about future milestones → that milestone's Notes;
   - Self-report unverified claims no reviewer could see from the diff
     (runtime, integrations, data) → never dismissed: they become the
     testing doc's "Watch points".
   Fixes go to an implementer and must be MINIMAL: reviewers invent
   hypotheticals by design, and a fix more complex than the problem it
   removes is itself overengineering. If a fix breaks something and the
   cause isn't quickly found, roll back to the checkpoint (`git checkout
   HEAD -- <paths>` or `git reset --hard HEAD`) and try another approach.
5. **Verify** after the fixes: full build and entire test suite, green
   before moving on.
6. **Second round (only if round 1 changed code):** ONE fresh
   `adversarial-reviewer` (same model and fallback) on
   the fix diff (`git diff HEAD -- . ':!docs/handoff'`), asking whether
   the fixes added defects or bloat. Same filter; fix what survives;
   verify again. **Hard cap: two rounds.** Anything a later look would
   find goes to the milestone's Notes — past two passes, review starts
   inventing bugs.
7. No surviving findings: say so and move on — don't invent changes to
   justify the gate. Keep the checkpoint either way.

## Handoff — when the session cannot close the milestone

If the session must end before the milestone reaches "Closing" (context
filling up, external blocker, user-requested pause):

1. Update `docs/handoff/M-XX.md` (create it and `docs/handoff/` only if
   missing):

   ```
   # Handoff — M-XX: [milestone title]

   ## Done
   - [concrete items completed, with file paths where relevant]

   ## Remaining
   - [remaining items from the acceptance criteria, in implementation order]

   ## Decisions made
   - [design or scope decisions not captured in docs/decisions/ — or "None"]

   ## Gate status
   - Build: [green / red / not run yet]
   - Tests: [green / red / not run yet]
   - Adversarial review: [not started / round 1 done (N findings) / skipped by policy]

   ## Next step
   [ONE sentence: the exact action the next session should start with]

   ## Implementer brief
   [Written at plan approval ("Delegated implementation" step 1). Kept
   as-is; new decisions go under "Decisions made".]
   ```

2. Commit it with any work in progress: `git add -A && git commit -m
   "wip(M-XX): handoff — [one-line reason]"`. NEVER push it.
3. Tell the user the next `/next-milestone` session will find it. Do not
   start another milestone.

## Closing — handing over for manual testing

Once the gate is passed and verified green:

1. **Write `docs/testing/M-XX.md`** in two tiers. The agent does
   everything it possibly can; the user does only what is impossible for
   the agent. For each candidate step ask: (a) could I verify this
   mechanically? → verify it now and leave it out of the doc; (b) can I
   drive it myself against the running app? → tier 1, executed in step 2
   and recorded; only what fails both is tier 2, for the user. Keep tier 2
   SHORT (aim for ≤ 5 steps; if longer, split "Essential" / "If time
   allows") and never pad it with steps that re-confirm what automation
   already proved. An empty tier 2 is legitimate. Sections:
   - **Verified by the agent:** tier-1 steps, each with what was driven
     and what was observed — a record to skim, not a script to run.
   - **How to test:** tier-2 steps only — numbered, concrete (what to open,
     click, type), each saying in a few words WHY it needs the user.
   - **Expected results:** per step or criterion, tied to the acceptance
     criteria.
   - **Not yet testable:** anything deferred to later milestones.
   - **Watch points:** the unverified claims from triage, each tied to
     the step that exercises it — test these hardest. "None" if empty;
     never omitted.
   - Any section the stack reference's `next-milestone / testing doc`
     section adds.
2. **Execute tier 1 now**, against the real running app — the environment
   the user would test in (the deploy, or the Editor/build they'd open).
   Not optional, not a dry run.
   - Possible for the agent: anything drivable through the harness's tools.
     Web: browser automation (the `claude-in-chrome` tools in the user's
     logged-in Chrome — state-changing actions inside the app under test
     are in scope, settings outside it are not), API probes with the
     project's tokens, DB queries. Other stacks: what the stack reference's
     `next-milestone / agent-executed testing` section lists. Any stack:
     waiting on a scheduled job; creating test data — then cleaning it up
     and leaving the app in the state the script says (or the state you
     found).
   - Impossible for the agent — the only things left for the user: a real
     device (phone, installed PWA, touch, device build, gamepad); physical
     actions (unplug the network, walk in front of a camera); accounts or
     roles the agent doesn't hold; subjective judgment (visual polish, game
     feel, tuning). When unsure, try it first and hand it over only if you
     actually couldn't.
   - Record each result under "Verified by the agent": passed (what was
     observed) or FAILED. A failure is a bug, not a user step: delegate the
     fix, verify, re-execute. Never hand the user a step you saw fail.
   - If a tier-1 step needs something only the user can grant (a browser
     permission, a tool the stack reference requires, a token), ask in one
     line and continue once it's there — never demote the step to avoid
     asking.
3. **Hand over in chat.** REPRODUCE tier 2 inline — full "How to test"
   steps and expected results; the user must not need to open a file. Then:
   the testing doc's path (one line); a compact tier-1 summary (one line
   per step: driven, observed); the gate summary (found, fixed, dismissed);
   one line on what the Self-report left unverified and which step covers
   it; and any reminder the stack reference's testing-doc section asks for.
   Then STOP: no further commits, never push, don't start the next
   milestone.
4. **Triage the user's comments** together:
   - **Covered by a future milestone** → confirm the M-ID, note it in that
     milestone's Notes.
   - **Small fix, in scope** → delegate (or the one-obvious-edit
     exception), verify, update the testing doc if steps changed.
   - **Design change** → stop implementing; update docs/milestones.md and
     add a decision record BEFORE any further code. Code follows docs.
5. Only after the user's explicit green light, direct them to
   `/close-milestone`.
