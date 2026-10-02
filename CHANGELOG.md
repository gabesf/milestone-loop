# Changelog

All notable changes to this project are listed here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `scripts/measure-sessions.py`: measures a project's sessions from the
  Claude Code transcripts — model calls (de-duplicated), active time
  versus waits (user, subagents, a resumed agent, a sleeping machine),
  context size, capture time, images, AskUserQuestion calls.
  `/close-milestone` appends one line per milestone or group to
  `docs/metrics.jsonl`, summing every session since its first `wip`
  commit (never to the Retro); `/milestone-status` shows the trend.
  Subagent descriptions now start with the unit and the role
  (`M-XX implementer`, `M-XX review: <lens>`, …) so the script can tell
  them apart. Baseline in `docs/measurements.md`.
- `Size: S` light track for small changes (conventions, "Small
  milestones"): behavior-only criteria, the orchestrator may make a
  few-line change itself, one test where a seam exists, at most one
  capture, the `/hotfix` mini-gate instead of the full gate, no testing
  doc, a one-line Retro. Set by `/plan-milestones` and `/replan`, or
  proposed in `/next-milestone`'s plan and written into the Notes on
  approval. In `/next-group`, an S member still gets an implementer.
  Untagged milestones are unchanged.
- Conventions, "Talking to the user": short messages, detail in files, and
  a closing block of at most five lines (decided / needs you / next) at
  the end of every step. Decisions with a recommended option that is
  cheap to undo are made, recorded and listed instead of asked, including
  an implementer's BLOCKED; the workflow's gates and one-time offers stay
  questions. Decisions taken this way reach the milestone's Deviations.
- Open design decisions are settled before the plan: when a criterion
  leaves a visual parameter open or has a "doesn't fit → BLOCKED" clause,
  `/next-milestone` (and `/next-group`, per member; one at a time on a
  single-runtime stack) runs a spike that
  measures the options and shows them in one composite image; the
  approval picks one.

### Changed

- `/next-milestone` plans fit one screen (one line per step), and the
  hand-over keeps tier 2 in full but summarizes tier 1 and the gate in
  four lines (tier 1, the gate, what stays unverified).
  `/plan-milestones` presents a summary with links instead of the
  documents.
- Every fix round (gate, feedback, BLOCKED) goes to a fresh implementer
  with the brief, the diff command and the findings, never one resumed
  with SendMessage — resumed implementers reached 600–970k of context and
  stalled. Implementers keep their context lean: quiet test reporters,
  files read by excerpt, never docs/milestones.md, downscaled screenshots.
  The prompt no longer re-reads CLAUDE.md where the host already loads it.
- Process requirements live once in
  `docs/guidelines/checkpoint-checklist.md`, which implementers go
  through before reporting and reviewers receive; the testing doc applies
  its testing rules; acceptance criteria no longer copy them.
  `/close-milestone`'s escalation check writes lessons there instead of
  CLAUDE.md, and warns when CLAUDE.md passes 15 KB (it is loaded into every
  agent). `/plan-milestones` keeps queue status and history out of
  CLAUDE.md.
- Cheaper runtime verification. `stack-web` plans a harness once (direct
  entry into app states, one capture command writing a downscaled contact
  sheet, raw captures git-ignored) and a DOM test environment; captures
  cover only what a criterion changes, at the sizes it names.
  `stack-unity` plans an Editor proof harness (seek to a point, faster
  time, logged values, one contact sheet) and asks once whether agents get
  their own Editor (`Agent editor:`); a busy Editor is reported at once.
  `/next-group` runs tier-1 testers at the same time when each can drive
  its own headless browser.
- Gate: the second round runs only when round-1 fixes changed runtime
  code (source, styles, shaders, scenes, assets), not docs, comments or
  tests alone. Doc and comment findings count only when the text is false
  about the code (leftovers such as TODOs still count), and are fixed in
  one batch; the reviewer agent no longer flags wording or docs written
  after the review.
- On macOS, `/next-milestone` and `/next-group` keep the machine awake
  (`caffeinate`, 8-hour limit, one at a time, pid file under the git dir)
  while agents work, and release it at every hand-over or handoff. A sleeping Mac had cut off running agents for
  hours in one group.
- Milestone archive (new default): `/close-milestone` moves each closed
  section to `docs/milestones-archive.md`; `docs/milestones.md` keeps the
  summary table (with `Covers`) and the open work. The escalation check
  greps both files, `/milestone-status` greps the archive for notes about
  open milestones, and G-IDs and M-IDs in the archive are never reused. A
  milestone that ran alone releases its group's open partners. Projects
  with closed sections already in `docs/milestones.md` are asked once, at
  their next close (archive them and delete leftover handoffs, inside that
  close's commit); declining records `Milestone archive: no` and keeps
  the old layout. `/replan` records each revision in one line.

## [0.7.0] - 2026-09-30

### Added

- Several stacks per project: `Stack: mechanical, electronics, web`
  loads every listed reference, in order. Hotspots and testing-doc
  sections combine, any serial group mode wins, contradictions are asked
  once and recorded in CLAUDE.md. Single-stack projects are unchanged.
- `stack-mechanical`: FreeCAD through its MCP server, a `Fabrication:`
  line with the user's processes, re-runnable geometry scripts as the
  source of truth, interference and clearance checks, options sheets for
  design decisions, fabrication files only after preview approval, serial
  groups. Simulation picked by the question (FEM in FreeCAD for strength,
  MuJoCo for mechanisms), scripted in `sim/`, validated against a hand
  calculation, checked for convergence.
- `stack-electronics`: PlatformIO, a probe firmware first, one pin header,
  host-tested logic, a recorded safe state per output, watchdog, sensors
  checked against a reference, unambiguous flashing, no flashing in
  worktrees.
- `physical-build`, shared by both physical stacks: `Kind: design` and
  `Kind: build` milestones, parts check before a build starts, a Hazards
  section in every testing doc, failsafe milestones first, dimension
  provenance (measured beats modelled), `docs/bom.md`, and an as-built
  record (`docs/as-built/M-XX.md`) that closes every build milestone.

### Changed

- `/replan` loads the stack reference, so milestones it adds carry the
  tags the stack requires (e.g. `Kind:` and `Parts:`).
- `/next-milestone` feedback triage also applies the stack reference's
  `next-milestone / feedback triage` section.
- Subagents get the path of every reference loaded for their step,
  shared ones included.

## [0.6.2] - 2026-09-29

### Added

- Local-only projects: `/app-overview` asks whether the workflow's commits
  are pushed to the remote or stay local, and records `Push: yes` or
  `Push: no` in CLAUDE.md. Under `Push: no` every skill commits without
  pushing, pulling or opening pull requests, and `/close-milestone`
  updates `main` locally. Skills that push ask when the line is missing.

### Changed

- `/next-group` ends its plan with a summary table (member → two-line
  summary) right before the approval question, instead of a separate
  summary inside each member's plan.

## [0.6.1] - 2026-09-29

### Changed

- Commit mode is now asked, not assumed: `/plan-milestones` asks whether
  milestones close through a direct push or a pull request (recommended
  for team work) and records `Commit mode: direct` or `Commit mode: pr` in
  CLAUDE.md. `/close-milestone` asks when the line is missing, and the
  legacy migration derives it from the old prose, so a project that used
  PR mode no longer silently switches to direct pushes.
- `/app-overview` and `/plan-milestones` offer to install `/grill-me` when
  they suggest the grill pass and it is missing, instead of only
  mentioning it.
- `/next-group` is marked beta: it tells the user so at the start and
  points to `/next-milestone` per member as the fallback.

## [0.6.0] - 2026-09-28

### Added

- Legacy check: every skill that reads `docs/milestones.md` stops on a
  project labeled by the pre-0.5 in-house workflow (Portuguese labels
  such as `Notas` or `TDD: sim`, which the skills would otherwise miss
  without an error) and offers a one-commit migration to the English
  labels.
- Parallel groups: two or three independent milestones implemented at
  the same time, each by its own implementer, then tested and closed
  together. Groups are recorded as a `Group: G-XX` tag in the members'
  Notes.
- `find-parallel` skill: finds and tags groups by dependency and by the
  files each milestone is expected to touch. `plan-milestones` applies
  its analysis to every new plan.
- `next-group` skill: one plan approval for the group, one git worktree
  and implementer per member (one after another in one tree on Unity),
  a review gate per member, an integration check on the merged result,
  and one manual test script of at most 5 steps for the whole group,
  with the criteria left out listed as accepted risks.
- Cross-milestone integration lens for the `adversarial-reviewer` agent.

### Changed

- `close-milestone` closes a group as one commit per member.
- `hotfix` and `replan` stop when local `wip` commits exist, since their
  push would publish them (the conventions' new checkpoint check).
- `replan` dissolves the groups its revision affects.

## [0.5.0] - 2026-09-23

First public release, extracted from a private in-house plugin.

### Added

- Workflow skills: `app-overview`, `plan-milestones`, `next-milestone`,
  `close-milestone`, `hotfix`, `replan`, `milestone-status`.
- `adversarial-reviewer` agent for the review gate in `next-milestone`
  and `hotfix`.
- `conventions` reference: stack loading, language and labels, the
  approver, model tiers, integration branch, git safety. The workflow
  skills point to it instead of repeating these rules.
- Stack references `stack-web` (Supabase + Next.js) and `stack-unity`.
- Model tiers (`top`, `standard`) mapped to model aliases in the
  project's CLAUDE.md, with defaults in the conventions reference.
- `Language:` line in CLAUDE.md for the prose of docs and chat,
  including milestone titles; file labels and commit message forms stay
  in English.
- CLAUDE.md settings lines: `Review gate: all | tagged | none` (written
  by `plan-milestones`) and `Commit mode: pr` (optional, set by hand).
