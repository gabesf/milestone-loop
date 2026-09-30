---
name: next-group
description: (Beta) Runs a parallel group of milestones (tagged `Group: G-XX` by
  /find-parallel or /plan-milestones) in one session. Plans every member
  for a single approval, gives each member its own implementer in its own
  git worktree (one after another in one tree on stacks that need it), runs
  each member's adversarial review gate, merges the members and verifies
  the combination, then hands the user ONE short, risk-ranked manual test
  script for the whole group. Only makes local, never-pushed checkpoint
  commits; /close-milestone closes the group.
disable-model-invocation: true
---

# Implement a parallel group

> **Beta.** Parallel groups are new and less tested than `/next-milestone`.
> Before anything else, tell the user: "`/next-group` is a beta feature.
> If anything goes wrong, you can run each member with `/next-milestone`
> instead." Then continue.

Run a group of independent milestones as one unit: one plan approval, one
implementer per member working at the same time, one review gate per
member, one integration check, and one manual test session for the whole
group. This session's job is the same as in `/next-milestone`: it
orchestrates and judges and never writes code. It does that for two or
three milestones at once.

This skill reuses `/next-milestone` instead of repeating it. Read
`../next-milestone/SKILL.md` (relative to this skill's base directory, or
the `next-milestone` skill by name on hosts that don't state it). Apply its
two opening rules to everything, and these sections to each member, with
the overrides below: "Delegated implementation", "Quality gates" and
"Adversarial review gate". Its "Closing" applies to the group as a whole
(see "Testing"). Its Preflight, Plan and Handoff sections do not apply:
this skill's own replace them.

Three more rules run through every section:

- **The context is the budget.** This session holds several milestones
  through planning, gates, testing and feedback. Never load a diff
  (reviewers fetch their own), keep build and test output to the tail
  (the last ~20 lines and the exit code), and delegate tier-1 driving
  (Testing, step 1).
- **Worktree discipline.** A subagent's Bash working directory resets on
  every call. Every prompt for a subagent working in a worktree gives the
  worktree's absolute path and says: start every Bash command with
  `cd <worktree> &&`, read and edit only by absolute paths under the
  worktree, and never edit the main tree.
- **Member commits hold member work only.** This session's own docs (the
  handoffs, the testing doc, docs/milestones.md) live in the main tree
  and are committed only in `wip(group)` commits. Every `wip(M-XX)`
  commit is staged with `git add -A -- <no-docs>`, which replaces
  `/next-milestone`'s `git add -A`; `<no-docs>` stands for `. ':!docs/handoff'
  ':!docs/testing' ':!docs/milestones.md'`. The live copy of a member's
  brief is the main tree's `docs/handoff/M-XX.md`: implementers read it
  there by absolute path, and the copy inside a worktree is never edited.

## Preflight

0. **Fresh-session check**, the same rule as `/next-milestone` Preflight 0.
1. `docs/milestones.md` must exist. If not, stop and point the user to
   `/plan-milestones`. Read the `conventions` reference
   (`../conventions/SKILL.md` relative to this skill's base directory, or
   the `conventions` skill by name) and run its "Legacy check".
2. **Identify the group.**
   - A `docs/handoff/G-XX.md` exists: that group is active, and it is the
     target (resumed or abandoned in step 4).
   - Otherwise, a single milestone `in-progress`: stop. One active unit at
     a time; the user finishes it with `/next-milestone` first.
   - Otherwise: the G-ID the user named, or else the first group, by its
     first member's position in the queue, whose members are all `open`
     and whose dependencies are all `done`. No `Group:` tags at all: stop
     and point to `/find-parallel`. Only one member still `open` (the
     others ran alone): stop and point to `/next-milestone`.
3. **Model-tier check (blocking)**, as `/next-milestone` Preflight 2,
   against the group's tier (conventions, "Parallel groups").
4. **Resume or abandon** (only when the group is active). Read
   `docs/handoff/G-XX.md` BEFORE asking anything, summarize it, check its
   Members table against `git worktree list` and `git -C <worktree>
   status --short`, and ask:
   - **Resume** from its "Next step", reusing the existing worktrees and
     `wip/M-XX` branches (never recreate them).
   - **Abandon:** `git worktree remove --force` each member's worktree,
     `git branch -D wip/M-XX`, then `git reset --hard <Base>`. That
     discards the group's local `wip` commits and puts every member back
     to `open`.
5. `git status` must be clean, as `/next-milestone` Preflight 4 says. Run
   the conventions' branch check now, before anything records a SHA.
6. Read CLAUDE.md fully. Load the stack reference as the conventions'
   "Stack reference" section says and apply its `next-milestone` sections
   and its `next-group` section; toolchain checks run NOW. The group's
   **mode** is serial when that `next-group` section says `Group mode:
   serial`, parallel otherwise.
7. **Re-check the group** (fresh start only) against the current code
   with `/find-parallel`'s Analysis (`../find-parallel/SKILL.md`): members
   still independent, footprints still disjoint in parallel mode. For a
   member that no longer fits, propose running without it; with the
   user's OK, continue without it. A group reduced to one member: stop and
   point to `/next-milestone`.

## Plan — one approval for the group

1. Read each member's acceptance criteria, covered requirements, notes and
   related decision records in docs/decisions/.
2. Present each member's plan as `/next-milestone` Plan 2 describes it,
   kept compact: what is built and which files it touches, how each
   acceptance criterion is met, and its tier. No per-member summary here:
   the summaries go in the closing table. Then the group block:
   - a footprint table (member → files and directories) showing the
     members don't overlap, and how each shared hotspot will be merged;
   - the merge order: queue order;
   - LAST, a **summary table** (member → its two-line summary, as
     `/next-milestone` Plan 2 describes it), so the user approves from one
     place without scrolling back through the member plans;
   - ONE closing question, as in `/next-milestone` Plan 2, on a single
     line right after the table: "Implementer model? (default: X)". The
     answer applies to every member and may name a different model for
     one of them. Never below the model floor.

   Write nothing before approval.
3. On approval:
   - write each member's brief to `docs/handoff/M-XX.md` exactly as
     `/next-milestone` "Delegated implementation" step 1 says;
   - write `docs/handoff/G-XX.md` from the template below, with `Base` =
     the current `HEAD` SHA;
   - mark every member `in-progress` in docs/milestones.md;
   - `git add -A && git commit -m "wip(group): start G-XX"`. NEVER push
     it. It makes the plan survive a dead session, and worktrees branch
     from it.

```
# Handoff — G-XX: [member IDs]

## Members
| Milestone | Phase | Worktree |
|---|---|---|
| M-XX | planned | .worktrees/M-XX (branch wip/M-XX) |

## Base
[SHA of HEAD before `wip(group): start`]

## Gate results
- M-XX: [rounds run; fixed: categories; dismissed: N] — Watch points: [unverified claims left for testing, or "none"]

## Integration
[not started / merged: M-XX, … / build and tests green / integration review: N findings, or skipped]

## Decisions made
- [decisions affecting more than one member — or "None"]

## Next step
[ONE sentence: the exact action the next session should start with]
```

Phases: `planned`, `implementing`, `gated`, `integrated`, `dropped`. In
serial mode the Worktree column says `main tree`. Update the file as each
member moves: it is how a resumed session knows where it is, and what
`/close-milestone` builds each Retro from.

## Implementation — parallel mode

1. **Worktrees.** Add `.worktrees/` to `.git/info/exclude` if it isn't
   there. That file is local to this clone and never committed; the entry
   keeps the worktrees out of the main tree's `git status` and `git add
   -A`. For each member: `git worktree add .worktrees/M-XX -b wip/M-XX`.
2. **Launch every implementer in ONE message** so they run at the same
   time. Prompt as `/next-milestone` "Delegated implementation" step 2
   says, plus: the worktree discipline above; the brief's main-tree path;
   first run the worktree setup (the stack reference's `next-group`
   section, or CLAUDE.md's install step); build and test only inside the
   worktree, leaving out what that `next-group` section defers to the
   integration check.
3. **On each return:**
   - check the main tree's `git status --short`: anything outside
     `docs/handoff/`, `docs/testing/` and `docs/milestones.md` leaked out
     of a worktree. Move it into the member's worktree and restore the
     main tree before anything else;
   - verify in the worktree: full build and entire test suite, minus the
     deferred part;
   - checkpoint in the worktree: `git -C <worktree> add -A -- <no-docs>`,
     then `git -C <worktree> commit -m "wip(M-XX): pre-review checkpoint"`.

   On BLOCKED, relay the question while the other members keep running.
   If the answer changes another member, the group was not independent:
   offer to drop this member. A member still red after two fresh
   implementers: offer to drop it ("Drop a member").
4. **Gate, per member:** `/next-milestone` "Adversarial review gate", with
   these changes:
   - the policy and tags are read per member;
   - launch all members' reviewers together;
   - each reviewer fetches its own diff: tell it to run `git -C <worktree>
     diff <Base> HEAD -- <no-docs>` (round 2: `git -C <worktree> diff HEAD
     -- <no-docs>`) and to read files under the worktree;
   - every git command of the gate, the rollback included, runs as `git -C
     <worktree>`; fixes go to an implementer in that worktree;
   - once the last round is verified green, commit its fixes in the
     worktree as `wip(M-XX): gate fixes` (nothing changed: no commit);
   - record the member's line under "Gate results": rounds, what was
     fixed, what was dismissed, and its watch points (the triage's
     unverified claims). Phase → `gated`.
5. **Merge**, in queue order, once every member is `gated` or `dropped`:
   - confirm the branch holds all the work (`git -C <worktree> status
     --short` is empty), then `git worktree remove .worktrees/M-XX`. Never
     `--force` here: a refusal means uncommitted work, so commit it first;
   - in the main tree: `git merge --squash wip/M-XX`, then `git commit -m
     "wip(M-XX): integrated"`, committing only what the merge staged;
   - **on a conflict:** `git reset --merge`. A squash merge leaves no
     merge in progress, so `git merge --abort` fails; `--merge` keeps this
     session's uncommitted docs. When both sides only add lines to a
     declared hotspot (a route, a menu entry), redo the merge, keep both
     sides, and `git add` the resolved files: that is the one-obvious-edit
     exception. Anything else: show the files and ask the user whether to
     delegate the resolution to an implementer or to drop the member;
   - after the last merge, `git branch -D wip/M-XX` for each merged
     member. Phase → `integrated`.

## Implementation — serial mode

No worktrees. The members go one at a time, in queue order, in the main
tree. Each goes through the whole cycle before the next one starts: its
implementer, verification, the checkpoint `wip(M-XX): pre-review
checkpoint`, its complete gate, `wip(M-XX): gate fixes`, and its "Gate
results" line. Its round-1 review diff runs from the parent of its first
`wip(M-XX)` commit to `HEAD`, `<no-docs>`; round 2 is `git diff HEAD --
<no-docs>`. Never run a reviewer while an implementer is working: the
reviewer would read a moving tree. Phase → `integrated` once gated.

## Integration check

Each member was verified alone; their combination has never been built.

1. If a member changed dependencies, re-run the project's install step in
   the main tree first. Then the full build and entire test suite, plus
   everything the stack reference's `next-group` section defers to this
   point. On red, send the failure output to a fresh implementer and
   commit its fix as `wip(M-XX): integration fix`, under the member whose
   files it changed.
2. **Integration review.** Run it only when the members share a hotspot
   file or a systems doc (their Docs lines), and not under `Review gate:
   none`. ONE `adversarial-reviewer` (standard tier's model) with the
   **cross-milestone integration** lens: conflicting assumptions between
   members, logic that two members each wrote because neither could see
   the other, and clashes over shared state or contracts. It gets the
   diff command `git diff <Base> HEAD -- <no-docs>`, which files belong to
   which member, the members' acceptance criteria, and CLAUDE.md. Same
   filter as the gate; minimal fixes, committed as `wip(M-XX):
   integration fix`; one round.
3. Update `docs/handoff/G-XX.md` (Integration, Next step). **Context
   seam:** all code is committed at this point, and "Gate results" holds
   what testing needs. If this session's context is already heavy, commit
   the docs as `wip(group): handoff — ready for testing` and tell the user
   to `/clear` and run `/next-group` again; the resumed session starts at
   Testing.

## Testing — one short script for the whole group

`/next-milestone` "Closing" applies to the group as a whole (two tiers,
execute tier 1, hand over, triage, green light), with these changes. The
testing doc is `docs/testing/G-XX.md`; the watch points come from "Gate
results".

1. **Tier 1 has no cap.** For each member, one tester subagent on the
   standard tier's model, one member at a time: there is one browser and
   one Editor. It gets the member's tier-1 steps, its criteria, the
   environment to test in (from CLAUDE.md), and the tools `/next-milestone`
   Closing step 2 names for this stack, and returns only the "Verified by
   the agent" record: each step, what was driven, what was observed,
   passed or FAILED. Screenshots and page dumps stay in its context. A
   FAILED step is a bug: delegate the fix, verify, re-run the step.
2. **Tier 2: at most 5 steps for the whole group.** 5 is a ceiling, not a
   target, and zero is valid. Candidates come from every member; take
   them in this order until the budget is full:
   1. **Must-have:** a criterion only a human can observe (visual result,
      feel, a real device, a physical action, an account the agent lacks)
      that no automated check or tier-1 step covers even in part, and any
      step the stack reference makes mandatory. A must-have is never cut.
   2. Watch points that only a human can exercise.
   3. Anything else only a human can check.

   Merge steps that share a setup into one walkthrough. Each step names
   the members it covers and, in a few words, the risk it checks. There
   is no "If time allows" list: a step that doesn't fit is an accepted
   risk (step 3). If the must-haves alone exceed 5, say so plainly: the
   group is too big for one test session. The user accepts the longer
   script or drops a member.
3. **Not manually tested (accepted risk):** a section of the testing doc
   with one line per criterion or watch point that neither tier covers,
   each naming its **proxy**: the tier-1 step or automated test that
   covers nearby behavior. A criterion with no proxy is a must-have, not
   an accepted risk. The hand-over shows this list, one line per item;
   the user may pull any of them into the script.
4. The other sections are as in `/next-milestone`: "Verified by the
   agent" and "Watch points" grouped by member, "How to test", "Expected
   results", "Not yet testable", and the stack reference's testing-doc
   sections.
5. **Feedback triage** as `/next-milestone` Closing 4, per member. Fix
   commits are named `wip(M-XX): fix — [what]`. One more outcome: the
   user won't approve a member now → drop it ("Drop a member") and
   continue with the rest.
6. Only after the user's green light for the group, direct them to
   `/close-milestone`.

## Drop a member

- **Before its merge:** `git worktree remove --force .worktrees/M-XX`,
  then `git branch -D wip/M-XX`.
- **After its merge, or in serial mode:** `git revert --no-commit` its
  `wip(M-XX)` commits, newest first, then `git commit -m "wip(M-XX):
  dropped"`. If the revert conflicts, `git revert --abort` and ask the
  user. Then rebuild, run the entire test suite, and re-run the tier-1
  steps of every member that shares a file the revert touched. If the
  member's migrations or other remote changes already went out, tell the
  user what now needs undoing.
- Either way: set the member back to `open`, remove its `Group:` tag,
  delete its `docs/handoff/M-XX.md`, mark its Members row `dropped`, and
  commit these docs as `wip(group): drop M-XX`. The remaining members
  continue, and `/close-milestone` closes them as the group, even if only
  one is left. Dropping the last remaining member is an abandon
  (Preflight 4).

## Handoff — when the session cannot finish the group

If the session must end before the hand-over (context filling up, an
external blocker, a user-requested pause):

1. Commit each member's uncommitted work as `wip(M-XX): handoff —
   [reason]`, staged with `<no-docs>`: in its worktree (parallel mode) or
   in the main tree (serial mode).
2. Update `docs/handoff/G-XX.md` (phases, Gate results, Integration,
   Decisions made, Next step) and each member's `docs/handoff/M-XX.md` as
   `/next-milestone` "Handoff" describes.
3. `git add -A && git commit -m "wip(group): handoff — [reason]"`. NEVER
   push it. Tell the user the next `/next-group` session resumes from it.
   Do not start anything else.
