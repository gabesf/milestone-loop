---
name: replan
description: Revises the milestone queue of a milestone-loop project. Reads
  docs/milestones.md, asks the revision objective, validates dependencies and
  requirement coverage, proposes a new queue, and commits the change. Does not
  touch in-progress milestones without explicit confirmation.
disable-model-invocation: true
---

# Revise the milestone queue

Read the project's milestone plan, ask what needs to change, propose a revised
queue with dependency and coverage validation, and commit the result.

## Preflight

1. `docs/milestones.md` must exist. If not, stop and point the user to
   `/plan-milestones`.
2. Read CLAUDE.md fully — integration branch, stack, review policy, and any
   project-specific rules that constrain milestone ordering or scope. Then
   read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it, and run its "Legacy check" and its **checkpoint
   check** ("Git safety"): this skill pushes. Load the stack reference as
   the conventions' "Stack reference" section says; its `plan-milestones`
   section's tagging rules apply to milestones this revision adds.
3. Read `docs/overview.md` if it exists — this is the canonical list of
   R-IDs. If it doesn't exist, coverage checks against R-IDs are skipped
   (warn the user once).
4. Scan milestones for state:
   - **`done`**: immutable by default. Never reopen, reorder, or edit a closed
     milestone unless the user explicitly asks and confirms. If the user's
     objective requires touching a done milestone, explain the consequence
     (Retro/Deviations records become stale) and get confirmation before
     proceeding.
   - **`in-progress`**: flag it to the user. Do not modify its status, scope,
     or position without explicit confirmation — someone may be mid-session on
     it.

## Process

1. **Ask the objective.** One clear question: "What is the goal of this
   queue revision?" Wait for the answer — the objective scopes everything below.
   Typical objectives: reprioritize, add/remove milestones, split/merge,
   react to a scope change, incorporate feedback from a completed milestone.

2. **Analyze the current queue.** Parse `docs/milestones.md`:
   - Build the dependency graph: any M-ID mentioned in a milestone's Notes as
     a dependency (e.g. "depends on M-03", "prerequisite for M-05", "after
     M-02", or the same in the project's Language) creates an edge. Report the graph to the user.
   - Build the coverage map: each milestone's **Covers** line lists the R-IDs
     it covers. Cross-check against the overview's R-IDs (Preflight §3).
   - Identify: uncovered R-IDs (plan bug), orphan R-IDs in milestones that
     don't exist in the overview (stale reference), dependency cycles, and
     milestones whose dependencies would be violated by a reorder.

3. **Propose the revised queue.** Present:
   - A before/after summary table (ID | Title | Status — old vs. new).
   - For each change: what changed and why (linked to the user's stated
     objective).
   - Dependency validation result: any ordering constraint violated? Any new
     dependency introduced?
   - Coverage check result: any R-ID newly uncovered or newly orphaned?
   - If the revision adds new milestones: draft the full section following
     the format in the existing file — Status, Covers, Acceptance criteria,
     Notes (with a `Tier:` tag, plus `TDD: yes` for engine/algorithm
     milestones, and `Adversarial gate: yes` for critical ones under
     CLAUDE.md's `Review gate: tagged`, when applicable, plus any tag the
     stack reference's `plan-milestones` section requires, e.g. `Kind:` and
     `Parts:` on physical stacks), and Docs.
   - If the revision removes milestones: confirm the R-IDs they covered are
     absorbed by other milestones — otherwise flag the coverage gap.
   - Group check: when the revision removes, reorders, or changes the
     scope or dependencies of an `open` milestone carrying a `Group:` tag,
     its group's independence no longer holds. Remove that tag from every
     `open` member of the group, and list the dissolved groups. New
     milestones get no tag.
   Wait for approval. Iterate on feedback.

4. **Apply the changes** to `docs/milestones.md`:
   - Update the summary table.
   - Update each modified milestone section.
   - Re-number M-IDs only if the user explicitly asks — renumbering is
     disruptive (Notes, decisions, handoffs, and commit history all reference
     the old IDs). Default: keep existing IDs and assign new IDs continuing
     from the highest existing number.

5. **Record the motivation.**
   - If the revision is a structural or design change (scope redefined,
     milestones fundamentally restructured): create an ADR in
     `docs/decisions/` — Context / Decision / Consequences.
   - Otherwise: add a line to the header of `docs/milestones.md`, above the
     summary table:
     `Revised (YYYY-MM-DD): <one-line motivation>`

## Closing

1. Commit on the integration branch with message
   `docs: queue revised on YYYY-MM-DD` and push (unless `Push: no`), under
   the conventions' "Integration branch", "Push" and "Git safety" sections.
2. Report what changed and which milestone is next in the queue. If
   groups were dissolved or milestones added, suggest `/find-parallel` to
   regroup.

## Rules

- The conventions' "Git safety" section applies in full; beyond its
  pull-before-push, this skill rewrites no history.
- Never modify milestone content beyond what the revision objective requires —
  this skill edits the queue, not the milestones' implementation details.
- Never start implementing a milestone. After committing, stop.
- If the revision would leave zero open milestones, confirm with the user —
  they may intend to add new ones.
