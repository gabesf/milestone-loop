---
name: milestone-status
description: Read-only dashboard of the project's milestone queue. Shows the
  queue summary, in-progress milestone, next open milestone with recommended
  model tier, accumulated notes/pendencies, and existing handoff files. Edits
  nothing. Runs fine on any model.
disable-model-invocation: true
---

# Milestone status — read-only dashboard

Show the current state of the project's milestone queue so the user can decide
what to do next without opening docs/milestones.md themselves.

Token note: this skill is read-only and mechanical, so the model floor does
not apply. It runs fine on any model — if the session is on the top tier's
model, mention once, at the start, that `/model` can downshift for this.

## Preflight

1. `docs/milestones.md` must exist. If not, stop and point the user to
   `/plan-milestones`.
2. Read `docs/milestones.md` fully.
3. Apply the `conventions` reference's "Legacy check"
   (`../conventions/SKILL.md` relative to this skill's base directory) as a
   warning only: this skill edits nothing, so on a hit, open the report by
   saying this is a legacy project whose tags this workflow misreads, and
   that `/next-milestone` will offer the migration.

## Report

Present the following sections in order, in the project's Language as
the `conventions` reference's "Language and labels" section says
(`../conventions/SKILL.md` relative to this skill's base directory).

### 1. Queue summary

Reproduce the summary table from docs/milestones.md (ID | Title | Status | Covers),
exactly as written — do not reformat or editorialize.

### 2. In progress

If exactly one milestone is `in-progress`:
- Show its ID, title, and acceptance criteria.
- Check for a handoff file at `docs/handoff/M-XX.md`. If it exists, read it
  and include a short summary: what's done, what's remaining, and the
  recommended next step. If no handoff exists, say so — the previous session
  left no state.

If more than one milestone is `in-progress` and a group handoff
`docs/handoff/G-XX.md` lists exactly those milestones as its members not
marked `dropped`, a parallel group is running: show the group ID, each
member's ID, title and phase, and the handoff's "Integration" and "Next
step". Otherwise, flag the inconsistency: list all of them and warn the
user that the state is invalid — only one milestone, or one group, should
be in progress at a time.

If no milestone is `in-progress`, say "No milestone in progress."

### 3. Next up

Show the first `open` milestone in the queue (same selection rule as
`/next-milestone`):
- Show its ID, title, and acceptance criteria.
- Look up the recommended tier and its model as the `conventions`
  reference's "Model tiers" section says (`../conventions/SKILL.md`
  relative to this skill's base directory). State both explicitly. If no tier is tagged, say "No
  recommended tier — use the session's default model."

If that milestone carries a `Group:` tag and every milestone with the same
tag is `open` with its dependencies `done`, show the group instead: its
ID, each member's ID and title, the group's tier (the highest member tier)
and its model, and the command `/next-group`.

If no `open` milestone exists, say "No open milestone in the queue."

### 4. Cross-milestone notes

Scan the Notes of ALL milestones in docs/milestones.md (done, in-progress,
and open; the archive is not read) for items
that reference OTHER milestones — deferred bugs, edge cases noted during
implementation, scope items moved from one milestone to another, dependency
warnings. List each one with the source milestone and the target milestone.

If none exist, say "No notes between milestones."

### 5. Trend

If `docs/metrics.jsonl` exists (written by `/close-milestone`), show its
last 5 lines as a table: milestone, date, wait on the user, implementer
active minutes (`implementer` + `fix`), implementer calls, capture
minutes, questions to the user, largest context. One line under it says
what moved most against the previous rows. No file: skip the section.

### 6. Other handoffs

List any files found in `docs/handoff/` that were NOT already shown in
section 2 (a running group's handoff and its members' briefs count as
shown). For each, show the filename and a one-line summary of its content
(read the file). If the directory does not exist, is empty, or all handoffs
were already covered above, say "No pending handoffs."

## Rules

- Never edit any file. This skill is strictly read-only.
- Never start a milestone. After reporting, stop.
- Never alter milestone status in docs/milestones.md.
- Never create, modify, or delete any file or directory.
- If CLAUDE.md does not exist, skip any checks that depend on it and note
  "CLAUDE.md not found" in the report.
