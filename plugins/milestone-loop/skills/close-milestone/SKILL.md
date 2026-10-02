---
name: close-milestone
description: Step 4 of the milestone-loop workflow. After the user's
  green light on manual testing, records the milestone's outcome (Deviations,
  Retro) in the docs, squashes the local wip(M-XX) checkpoint, and commits
  and pushes the milestone to the project's integration branch (dev by
  default) as a single commit, then verifies the result in git. Closes a
  parallel group the same way, one commit per member.
  The only skill that pushes milestone work (nothing is pushed under
  `Push: no`).
  When the last milestone closes, offers to update main.
disable-model-invocation: true
---

# Close a milestone

Record the milestone's outcome in the docs and commit the work. This skill
runs only after the user has manually tested and explicitly approved — it is
the second human gate of the workflow. The whole close runs in this session.

## Preflight

1. Exactly one milestone must be `in-progress` in docs/milestones.md,
   or, when a group handoff `docs/handoff/G-XX.md` exists, exactly that
   group's members not marked `dropped`: **group mode** (see "Closing a
   group"). In group mode, note the handoff's `Base` SHA now; Close
   deletes the file. If none, ask which milestone this is about; if the
   state looks inconsistent, show the user and resolve together before
   committing anything.
   Exception: if ALL milestones are already `done`, skip straight to
   "Project completion" below — the user is here to update `main`.
2. Read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it. Run its "Legacy check" now. Its "Integration
   branch" and "Git safety" sections bind every git command below.
3. Confirm explicitly: "Have you tested M-XX and do you approve closing
   it?" (group mode: name the group and every member). A green light
   given earlier in this same session counts; a green light assumed from
   context does not. Then run the conventions' **branch
   check**.
4. Load the stack reference as the conventions' "Stack reference" section
   says; its `close-milestone` section holds pre-commit checks (step 3 of
   "Close").
5. Check CLAUDE.md for a `Push:` line; no line: ask as the conventions'
   "Push" section says and record the answer. Under `Push: no` the commit
   mode is `direct` and every push below is skipped.
6. Check CLAUDE.md for the project's commit mode: **PR mode** with a
   `Commit mode: pr` line, **direct** with `Commit mode: direct`. No line:
   ask as the conventions' "Commit mode" section says and record the
   answer in CLAUDE.md; the close commit carries it.
7. **Archive offer (once per project).** When `docs/milestones.md` still
   holds sections of `done` milestones, `docs/milestones-archive.md` does
   not exist, and CLAUDE.md has no `Milestone archive:` line, offer to
   clean up now, in one commit `docs: archive closed milestones` made
   before the close (branch check first; pushed with the close):
   - move every `done` section to the archive (conventions, "Milestone
     archive");
   - delete handoffs left over from `done` milestones, listed first;
   - if image files are committed under `docs/` beyond the contact sheets
     the testing docs link, untrack their folders (`git rm -r --cached`,
     plus a `.gitignore` entry); the files stay on disk.
   The user may take any part. On no, record `Milestone archive: no` in
   CLAUDE.md (the close commit carries it) and never offer again.

## Compose the record

1. **Deviations** line, when the implementation differed from the plan (scope
   moved, criteria adjusted, comments deferred to other milestones).
   "None" is a valid entry; silence is not — future sessions rely on this
   being trustworthy.
2. **Retro:** line with three data points: (a) what the adversarial gate
   caught (confirmed findings that led to fixes — categories, not every
   item); (b) what only the user's manual testing caught ("none" if the
   user reported nothing); (c) how many rounds the gate ran (0 if skipped
   by CLAUDE.md policy, 1 or 2 otherwise). "None / none / 1 round" and
   "n/a / none / 0 rounds (gate skipped)" are valid; omitting the line is
   not. A `Size: S` milestone keeps the three data points to one short
   line. If this session did not run `/next-milestone` for the milestone
   (fresh session after a handoff), reconstruct (a) and (c) from
   `docs/testing/M-XX.md`'s "Watch points", `docs/handoff/M-XX.md` and
   the `wip(M-XX)` commit, and ask the user for (b) — never invent a Retro.
   Group mode: one Retro per member. Each also names the group and adds
   (d) its accepted risks, the member's criteria listed under the testing
   doc's "Not manually tested (accepted risk)" ("none" if empty), so a
   later escape can be traced to the test budget. Count the integration
   review's findings once, on the last member. Take (a) and (c) from the
   group handoff's "Gate results" and "Integration", (d) from
   `docs/testing/G-XX.md`.
3. **Escalation check.** Scan the Retro lines of previously closed
   milestones (grep `docs/milestones.md` and `docs/milestones-archive.md`). If the same category of escape appears in 2 or more (e.g.
   "visual bug the gate missed" recurring), suggest a line that would
   prevent it (a review-lens hint, a testing-doc rule, a build-time check)
   for `docs/guidelines/checkpoint-checklist.md` — create it and link it
   from CLAUDE.md's doc index if missing. CLAUDE.md gets a rule only when
   every agent needs it on every call: it is loaded into all of them. The
   user decides; if yes, apply it now so the commit picks it up.
   **CLAUDE.md size.** If CLAUDE.md is over 15 KB, say so and propose what
   to move out: queue status and history (docs/milestones.md has them),
   dated lessons (to the checklist). The user decides; apply now if yes.
4. **Decisions backstop.** If a design change from the user's feedback is
   not yet recorded, write its decision record in `docs/decisions/` now.

## Close

1. **Docs edit.** In `docs/milestones.md`, set the milestone to `done` and
   add the Deviations and Retro lines under it, matching the file's existing
   formatting. Then, unless CLAUDE.md says `Milestone archive: no`, move
   its whole section to the end of `docs/milestones-archive.md` (create it
   with a `# Milestones archive` heading and add the link under the
   summary table, as the conventions' "Milestone archive" section says);
   the table row stays, marked `done`.
   **Metrics.** Then append one line to `docs/metrics.jsonl` (create it if
   missing) with the output of `python3 <plugin>/scripts/measure-sessions.py
   "<project root>" --latest --jsonl --milestone M-XX` (group mode:
   `--milestone G-XX`), where `<plugin>` is `../..` from this skill's base
   directory. It reads this session's transcripts and prints one JSON line:
   waits on the user and on subagents, active minutes per role,
   implementer calls, the largest context, capture minutes, questions to
   the user. If the script is missing or fails (another host, no
   transcripts), say so in one line and go on: metrics never block a close,
   and they never go into the Retro.
2. **Handoff deletion.** If `docs/handoff/M-XX.md` exists, delete it (and
   `docs/handoff/` if it is then empty). Stage with `git add -A` so the
   deletion is in the commit.
3. **Stack pre-commit checks.** Run the stack reference's `close-milestone`
   checks against everything the commit will contain. Handle findings as
   that section says and tell the user what changed; a finding it doesn't
   say how to handle is settled with the user before committing.
4. **Squash the checkpoint.** `/next-milestone` leaves local `wip(M-XX)`
   commits (never pushed). Fold them into the final commit so the
   integration branch keeps one commit per milestone:
   - List local-only commits: `git log @{u}..HEAD --oneline` (no upstream
     yet, or `Push: no`: `git log --oneline` back to the last `M-` commit).
   - **Safe to squash** only if every local-only commit is `wip(M-XX)` for
     THIS milestone and none exists on the remote. Then `git reset --soft
     <parent of the first wip(M-XX) commit>` — the whole milestone stays
     staged as one change.
   - No `wip` commit (older milestone): proceed normally.
   - Anything else — a `wip` from another milestone, a `wip` already on
     the remote, interleaved foreign commits: rewrite nothing; show the
     user the state and resolve together.
5. **Commit and push.** Stage everything again (`git add -A`) so the
   stack checks' changes are included, then:
   - **direct**: commit with message `M-XX: [milestone title]` and push
     to the integration branch, pulling first as the Git safety rules say
     (`-u` and no pull if the branch check just created it). Under
     `Push: no`: commit only.
   - **PR mode**: create branch `milestone/M-XX`, commit, push, and open a
     PR to the integration branch titled `M-XX: [milestone title]` with the
     acceptance criteria and the Deviations text in the description.
6. **Verify in git:**
   - `git status --short` is empty;
   - `git log -1 --oneline` is `M-XX: ...` on the integration branch (PR
     mode: on `milestone/M-XX`);
   - `git log @{u}..HEAD` is empty — nothing left unpushed (skip under
     `Push: no`);
   - `git log --oneline -5` shows no `wip(` commit;
   - the summary table shows the milestone `done`, and its section (in
     the archive, unless `Milestone archive: no`) has both lines.
   A failed check is reported to the user with the state, not patched over.
7. **Report**, as the conventions' "Talking to the user" closing block:
   milestone closed (hash, branch, PR URL in PR mode) and which
   milestone is next (or which group, when the next open milestone carries
   a `Group:` tag and its group can run now; the command is then
   `/next-group`). State the next milestone's recommended tier and its
   model (conventions, "Model tiers") — the user needs it now to set
   `/model`; if none is tagged, say so instead of
   guessing. Remind the user: `/clear`, set `/model`, then
   `/next-milestone`. Do not start it yourself.

## Closing a group

Group mode (Preflight 1) runs the same Close steps with these changes:

- **Step 1:** edit every member's section. A `dropped` member stays
  `open` and untouched.
- **Step 2:** delete `docs/handoff/G-XX.md` and every member's handoff.
- **Step 4: split instead of squash.** A group's local `wip` commits mix
  members (merges, then fixes), so they are split back into one commit per
  member:
  1. `git add -A && git commit -m "wip(group): close"`. Save that commit's
     SHA as **S**: the rollback point, and exactly the tree that must end
     up committed.
  2. Check `git log --format='%h %s' <Base>..S`. Split only if every
     commit is `wip(group)` or a member's `wip(M-XX)`, and none is on the
     remote. Anything else: rewrite nothing; show the user the state and
     resolve together.
  3. File sets. The files to commit are those in `git -c
     core.quotePath=false diff --name-only --no-renames <Base> S`; ignore
     any other path. Attribute them with `git -c core.quotePath=false log
     --no-renames --name-only --format='@@ %s' <Base>..S`: a member's set
     is every listed file its `wip(M-XX)` commits touch. A file in two
     sets belongs to the later member. A `dropped` member gets no set and
     no commit; a file it shared stays with the member that shares it.
     `docs/handoff/`, `docs/testing/` and `docs/milestones.md` belong to
     no member: they go with the last commit.
  4. `git reset --soft <Base>`, then `git reset -q`: everything unstaged,
     working tree untouched. PR mode: `git checkout -b group/G-XX` now, so
     the member commits never land on the integration branch.
  5. For each member in queue order except the last: `git add -A --
     <its files, each quoted>`, then commit `M-XX: [milestone title]`. The
     last member: `git add -A` (its files plus all docs), then commit.
  6. **Invariant, before any push:** `git diff --quiet S HEAD` succeeds,
     `git status --short` is empty, and `git log --oneline <Base>..HEAD`
     shows exactly one `M-XX:` commit per member not `dropped`, in queue
     order. Otherwise run `git reset --hard S` (PR mode: first `git
     checkout -f <integration branch>`, then reset it, then `git branch -D
     group/G-XX`) and stop: show the user the state, never patch a split
     by hand.
- **Step 5:** direct: push once, after the last commit (`Push: no`: no
  push). PR mode: push
  `group/G-XX` (created in the split) and open one PR to the integration
  branch titled `G-XX: [member IDs]`, with each member's acceptance
  criteria and Deviations.
- **Step 6:** `git log --oneline` shows one `M-XX:` commit per member
  not `dropped`, in queue order, and no `wip(`; each of those members
  shows `done` with both lines.

## Project completion — updating `main`

If `main` IS the integration branch, this is a no-op: when the last
milestone closes, tell the user the project is complete. Otherwise `main`
only receives the finished project. If no milestone is left `open` or
`in-progress`, tell the user the project is complete and ask: "All
milestones are done. May I update `main` with the integration branch?"
Only with a yes — first check that `main` exists (`git ls-remote --heads
origin main`; under `Push: no`, `git rev-parse --verify main`):

- **No `main` yet** (the repository's first commit was made on the
  integration branch), either mode: create it from the integration branch
  with `git push origin <integration branch>:main` (`Push: no`: `git
  branch main <integration branch>`); nothing to merge or review.
- **direct**: `git checkout main && git pull --rebase`, merge the
  integration branch, `git push`, then check the integration branch out
  again. Pull BEFORE the merge, never after: rebasing a merge replays
  already-pushed commits. Under `Push: no`: no pull and no push, only the
  checkout, merge and checkout back.
- **PR mode**: open a PR from the integration branch to `main` titled with
  the project name; do not merge it yourself.

If the user declines (e.g. final validation still pending), leave
everything on the integration branch and tell them to re-run
`/close-milestone` later — with all milestones `done`, the skill performs
only this step.
