---
name: hotfix
description: Fixes a bug found in real use, outside the milestone cycle.
  Reproduces (automated test when viable), applies a minimal fix, runs a
  mini-gate (1 adversarial-reviewer on the diff), commits fix:... to the
  integration branch, and pushes. Does not alter milestone status. Refuses
  scope that is not a fix — feature work goes through /replan.
disable-model-invocation: true
---

# Hotfix — fix a bug outside the milestone cycle

Apply a minimal, reviewed fix for a bug found in real use. This skill owns
the full path: reproduce → fix → mini-gate → commit → push. It never touches
milestone status and never expands scope beyond the reported bug.

## Preflight

1. CLAUDE.md must exist. Read it fully — build/test commands, integration
   branch, stack, review policy.
2. `git status` must be clean. If there are uncommitted changes, warn the
   user and ask how to proceed — a hotfix should start from a known state so
   its diff is isolated and reviewable.
3. Read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it. Run its "Legacy check" and its "Integration branch"
   check now — the fix is committed to the integration branch.
4. Run the conventions' **checkpoint check** ("Git safety"). A blocker
   for the work in flight is fixed inside its own `/next-milestone` or
   `/next-group` session.
5. **In-progress milestone check.** If `docs/milestones.md` exists and a
   milestone is `in-progress`, warn the user: a hotfix on the integration branch
   while a milestone session is open can cause merge friction. Ask whether to
   proceed anyway. (This is a warning, not a block — the user may be fixing
   a blocker for that very milestone.)
6. Load the stack reference as the conventions' "Stack reference" section
   says, and apply its `next-milestone / quality gates` rules during the
   fix.

## Process

1. **Bug description.** Ask the user to describe the bug: what they
   observed, what they expected, and how to trigger it. If the user already
   provided this when invoking the skill, acknowledge and proceed.

2. **Scope guard.** If the reported issue is not a defect in existing
   behavior but a request for new functionality, stop: explain that this is
   feature work, not a hotfix, and point the user to `/replan` to add it to
   the milestone queue. Do not proceed with implementation.

3. **Reproduce.** Write an automated test that demonstrates the bug (red)
   when the project's stack makes this practical. If automated reproduction
   is not viable (visual bug, hardware-dependent, integration with external
   service), document the manual reproduction steps instead and move on.

4. **Fix.** Apply the minimal change that corrects the defect. Minimal means:
   - Touch only the code paths responsible for the bug.
   - Do not refactor surrounding code, even if it's ugly.
   - Do not add features, even small ones that "make sense while we're here."
   - If the fix requires a design change, stop and tell the user — that
     belongs in a milestone, not a hotfix.

5. **Verify green.** Run the project's full build and test suite as
   specified in CLAUDE.md. The reproduction test (step 3) must now pass
   (green). All other tests must remain green — a hotfix that breaks
   something else is not a fix.

6. **Mini-gate — adversarial review.** Launch 1 `adversarial-reviewer`
   agent (`model` = the standard tier's model, conventions "Model tiers")
   against the hotfix diff (`git diff` from the integration branch's
   pre-fix state to the working tree). Assign the **bugs & correctness**
   lens plus the regression check the full gate gives the leftovers lens
   (every caller of a function the fix changes still works): this one
   reviewer covers both. Pass the agent:
   - The diff.
   - The acceptance criteria for this fix: a one-line statement of the bug
     being fixed and the expected correct behavior after the fix.
   - CLAUDE.md.

   Filter: discard findings below 80 confidence, pre-existing issues, and
   pedantic nitpicks. For each surviving finding: fix if real and in scope;
   dismiss with a one-line reason if not. If the fix changed code, re-run
   the full build and test suite. **One round only** — this is a mini-gate,
   not the full milestone gate.

7. **Milestone annotation.** If `docs/milestones.md` exists and the bug
   reveals a problem that a future milestone should address (incomplete
   acceptance criteria, missing edge case, design assumption that broke),
   add a note to that milestone's Notes. Do not change any milestone's
   status. If the file does not exist, skip this step.

8. **Commit and push.** Commit with message `fix: <short description of the
   bug>` and push to the integration branch (unless `Push: no`) under the
   conventions' "Push" and "Git safety" sections.

9. **Report**, as the conventions' "Talking to the user" closing block:
   what was fixed, which test covers it (if automated), and whether any
   milestone Notes were updated. If every
   milestone is `done` and the integration branch is not `main`, add how
   the fix reaches `main`: direct mode, through `/close-milestone` (it then
   runs only its `main` update); PR mode, through the integration → `main`
   PR if it is still open (the push already updated it), otherwise through
   `/close-milestone`.

## Rules

- Never alter milestone status in `docs/milestones.md`.
- Never expand scope beyond the reported bug. One bug = one hotfix session.
- The conventions' "Git safety" section applies in full.
- Never skip the mini-gate. The review policy in CLAUDE.md governs the full
  milestone gate in `/next-milestone`; the hotfix mini-gate is independent
  and always runs — a single reviewer on a small diff is cheap insurance.
