---
name: conventions
description: >-
  Shared conventions for the milestone workflow. NOT an invocable skill —
  the workflow skills (app-overview, plan-milestones, find-parallel,
  next-milestone, next-group, close-milestone, hotfix, replan,
  milestone-status) read this document via a relative path.
  Holds the rules they share: loading the stack reference, language and
  labels, legacy projects, the approver, model tiers, parallel groups, the
  integration branch, and git safety.
disable-model-invocation: true
---

# Workflow conventions

Rules shared by every workflow skill. A skill that points here applies the
sections it names with the same force as its own rules; where a skill states
a narrower rule for its own step, the skill wins for that step.

## Loading references

Reference skills (this one, the `stack-<stack>` ones, and the shared
references a stack reference names, such as `physical-build`) are not
invocable.
A workflow skill reads them as files: `../<name>/SKILL.md` relative to its
own base directory when the harness states that directory at invocation
(Claude Code does), or loads the skill by name through the harness's skill
mechanism otherwise (other Agent-Skills hosts).

A subagent has no skill base directory. When one needs a reference (this
one or a stack reference), pass it the absolute path of every reference
loaded for that step, shared ones included, or the skill name only when
the path is not known.

## Stack reference

1. CLAUDE.md records the project's stack with a `Stack: <stack>` line (e.g.
   `Stack: unity`), written by `/plan-milestones`. A project that mixes
   stacks lists them comma-separated, e.g. `Stack: mechanical,
   electronics, web`.
2. Load the stack reference `stack-<stack>` as described in "Loading
   references". Its sections are named after the workflow skill (and step)
   that applies them, e.g. `next-milestone / quality gates`. Apply the
   invoking skill's sections at the point its preflight says; they carry the
   same force as the skill's own rules, and any toolchain check they list
   runs then, before further work. A stack reference that names a shared
   reference (e.g. `physical-build`) loads it the same way, once per
   session even when several stack references name it, and its sections
   apply the same way.
3. **Several stacks.** Load the reference of every listed stack that has
   one. Wherever a skill says "the stack reference", read "each loaded
   reference": apply each one's section for that step, in the order the
   `Stack:` line lists them (shared references right after the first
   stack that names them). A step's hotspots, exclusions and testing-doc
   sections are the union of theirs. `Group mode: serial` in any one of
   them makes the group serial. When two references give contradicting
   rules for the same step, stop and ask the user which applies to this
   project, and record the answer in CLAUDE.md. CLAUDE.md's own rules
   override every reference.
4. No `Stack:` line: before `/plan-milestones` has run (no
   `docs/milestones.md`) that is normal — proceed without a stack
   reference. After it, the line is required: stop and ask the user which
   stack the project uses, and record the line before continuing.
5. A recorded stack with no reference for it: proceed without one (for
   that stack only, when several are listed).

## Language and labels

- **Labels are fixed English.** Every file the workflow writes or reads
  uses its labels exactly as the skills spell them: milestone fields
  (`Status`, `Covers`, `Acceptance criteria`, `Notes`, `Docs`,
  `Deviations`, `Retro`), tags (`Tier:`, `TDD: yes`, `Adversarial gate:
  yes`, `Group: G-XX`, `Size: S`, and `Kind: design` / `Kind: build` on
  physical stacks), CLAUDE.md lines (English even where no skill
  spells the label out), the headings of the overview, handoff, testing
  and decision docs, the phase values in a group handoff, and the `None` /
  `none` entries that mark an empty field. Skills parse these files, so a
  translated label breaks them.
- **Commit messages are English**, in the forms the skills give. A
  milestone's title appears in them as written.
- **Prose follows `Language:`.** CLAUDE.md's `Language: <language>` line
  (written by `/app-overview`) sets the language of everything else:
  document bodies, requirement and criteria text, milestone titles, and
  chat with the user — including the questions skills quote in English,
  which are asked in that language. No line: use the language the user
  writes in.

## Talking to the user

Applies to every message a workflow skill shows the user.

- **Short.** Say what happened and what it means in a few lines. Detail
  lives in files (handoff, testing doc, decision records) and is linked,
  not pasted. What the user must act on is the exception: tier-2 steps
  and questions are written out in full.
- **Closing block.** End every message that finishes a step or waits for
  the user with at most five lines, in the project's Language: what was
  decided on the user's behalf, what needs the user (or "nothing"), and
  what comes next. Many users read only this block, so it stands on its
  own.
- **Decide what is reversible.** Ask only about a decision that is hard to
  undo, or one with no option you can recommend. When an option can be
  recommended and a wrong choice is cheap to undo (a value, a placement, a
  wording, a visual detail), apply it, record it under the handoff's
  "Decisions made" (it reaches Deviations at close), list it in the
  closing block, and carry on: the user overrides it while testing. An
  open question holds the whole session, overnight if nobody is there.
- The workflow's gates stay questions: overview sign-off, plan approval,
  the green light to close, and anything that touches `main`.

## Legacy projects

Projects started on the pre-0.5 in-house workflow label their files in
Portuguese. These skills don't parse those labels, and nothing errors: a
`TDD: sim` tag is not seen, so TDD is skipped; a `Gate adversarial: sim`
tag is not seen, so under `Review gate: tagged` the gate is skipped.

**Legacy check.** If `docs/milestones.md` exists, search it for a field
label `**Cobre:**`, `**Critérios de aceitação:**`, `**Notas`, `**Desvios`
or `**Modelo:**`, or a tag `TDD: sim` or `adversarial: sim` (any case). A
hit means a legacy project: stop before any other work and offer the
migration below. Continue only once it is committed. If the user declines,
stop and tell them to run the pre-0.5 skills on this project.

**Migration** — one commit, with the user:

1. `docs/milestones.md`: rename field labels only (lines of the form
   `- **Label…:**`; bold words in prose stay): `Cobre` → `Covers`,
   `Critérios de aceitação` → `Acceptance criteria`, `Notas` → `Notes`,
   `Desvios` → `Deviations`, keeping any suffix (`**Desvios (13/09):**` →
   `**Deviations (13/09):**`). Tags: `TDD: sim` → `TDD: yes`,
   `Gate adversarial: sim` → `Adversarial gate: yes`. A `**Modelo:**` line
   becomes a `Tier: top` or `Tier: standard` tag in that milestone's Notes
   (top when it names the top-tier model); ask when it is unclear.
2. CLAUDE.md: legacy projects state the review policy, model tiers and
   commit mode in prose. Derive the `Language:`, `Review gate:`,
   `Model tiers:` and `Commit mode:` lines (plus `Model cap:` /
   `Implementation model:` when the prose says so) from it, confirm each
   value with the user, and add them. No commit mode in the prose: ask as
   the "Commit mode" section below says. Keep the prose.
3. Any `docs/handoff/M-XX.md`: rename the headings `Feito` → `Done`,
   `Faltando` → `Remaining`, `Decisões tomadas` → `Decisions made`,
   `Estado dos gates` → `Gate status`, `Próximo passo` → `Next step`,
   `Brief do implementador` → `Implementer brief`. The in-progress
   milestone's `docs/testing/M-XX.md`, if any: `Pontos de atenção` →
   `Watch points`.
4. Show the user the diff, then commit on the integration branch (branch
   check and Git safety below) as `docs: migrate to milestone-loop labels`.
   Don't push; the next push carries it. A dirty working tree: ask first.

## Approver

The **approver** signs off on the overview before planning starts: whoever
owns the product decisions (a client, a product owner). On a solo project
the approver is the developer; the gate still applies, as a deliberate
re-read of the finished overview before `/plan-milestones`.

## Model tiers

Skills speak of two tiers, never of model names:

- **top tier** — the strongest model. For milestones whose core is an
  engine/algorithm with subtle invariants, and for `/plan-milestones`.
- **standard tier** — a strong-reasoning model. For conventional milestones
  (screens, CRUD, reports, integrations), implementer subagents and
  reviewers.

CLAUDE.md maps tiers to model aliases (anything `/model` and the Agent
tool's `model` parameter accept), written by `/plan-milestones`:

- `Model tiers: top = <alias>, standard = <alias>`
- `Model cap: standard` — optional; the project never uses the top tier,
  so top-tier milestones run on the standard tier.
- `Model floor: <alias>` — optional; the weakest model accepted for a
  `/next-milestone` session or an implementer. Default: the standard
  tier's alias.
- `Implementation model: <alias>` — optional; the default implementer
  model. Default: the standard tier's alias.

**Defaults** (no `Model tiers:` line): top = `fable`, standard = `opus`.
If the user says `fable` is not available, top = `opus`: record
`Model tiers: top = opus, standard = opus` in CLAUDE.md so later sessions
don't ask again. A cheaper standard tier
(e.g. `sonnet`) is the user's call to record; this workflow is untested
with it.

Workflow skills launch the `adversarial-reviewer` agent with `model` = the
standard tier's model. The agent's own frontmatter pins `model: opus` (the
default standard tier) as the fallback for launches that pass no model;
users may change that line.

A milestone's recommended tier is the `Tier: top` or `Tier: standard` tag
in its Notes in docs/milestones.md, lowered to `standard` under a
`Model cap:`. No tag: no tier is recommended. To name the model for a
tier, resolve it through the mapping above.

**Comparing models.** A model is *below* a tier or the floor unless it is
that alias's model or one ranked above it (the top tier's model is above
the standard tier's). When the session cannot tell (a model outside the
mapping), ask the user instead of guessing.

## Small milestones (`Size: S`)

A milestone tagged `Size: S` in its Notes is one small change: one
behavior, no engine or algorithm (never with `Tier: top` or `TDD: yes`),
no open design decision, no schema migration or new dependency, and a
diff expected to touch a few files. The full workflow costs more than such
a change, so it runs a light track. `/plan-milestones` and `/replan` set
the tag; `/next-milestone` may propose it in its plan for an untagged
milestone that fits, and the approval settles it. No tag: every skill runs
its full track.

The light track:

- **Criteria** state the behavior only. Process requirements (runtime
  capture, docs sync, before/after proof) are not criteria; the project's
  checklist applies, scaled to the change.
- **Implementation.** A few edits in one or two files: the orchestrating
  session may make them itself, an exception to "does not write code".
  Anything larger: one implementer, as usual.
- **Tests.** One assertion of the new behavior where the project already
  has a place for it. Never new test infrastructure for an S change.
- **Runtime check.** Only for a visual criterion: one capture, at the
  project's default size, through the project's capture harness if it has
  one.
- **Docs.** Only the text the change makes false.
- **Gate.** The `/hotfix` mini-gate replaces the full gate: one
  `adversarial-reviewer` (standard tier's model) with the bugs &
  correctness lens, told to flag scope creep too; one round. The review
  policy still decides whether it runs.
- **Testing.** No testing doc. Tier-1 results and the tier-2 steps
  (usually one or two) go in the hand-over message.
- **Close.** Deviations as usual; the Retro's data points on one short
  line.

Several small changes the user asks for together are planned as ONE
`Size: S` milestone, one criterion each, rather than one milestone each.

## Parallel groups

A **group** is two or three `open` milestones that can be implemented at
the same time, each by its own implementer, and are tested and closed
together. `/find-parallel` (and `/plan-milestones`, which applies its
analysis) records a group as a `Group: G-XX` tag in each member's Notes —
the tag exactly, then free prose in parentheses. A group is every
milestone carrying the same tag. G-IDs are never reused (the archive's
tags count too, see "Milestone archive"), and `done`
milestones keep their tag as history. `/next-group` runs a group.

- **One active unit at a time:** one milestone (`/next-milestone`) or one
  group (`/next-group`). A group is active while its handoff
  `docs/handoff/G-XX.md` exists; several milestones `in-progress` at once
  are valid only when they are exactly that group's members.
- **Group tier:** the highest recommended tier among its members, resolved
  as "Model tiers" says.
- **Mode:** parallel — a git worktree per member — unless the stack
  reference's `next-group` section says `Group mode: serial`: members are
  then implemented one after another in the main tree.

## Milestone archive

`/close-milestone` moves each closed milestone's section (criteria,
Notes, Deviations, Retro) to the end of `docs/milestones-archive.md`.
`docs/milestones.md` keeps the summary table, with every milestone and
its `Covers` (done ones included), a link to the archive under the table,
and the sections of the milestones still `open` or `in-progress`. Agents
read the archive only when a step says so: the escalation check greps its
Retro lines, and M-IDs and G-IDs found there are never reused. Under
`Milestone archive: no` in CLAUDE.md, closed sections stay where they are.

## Integration branch

- Workflow commits (docs and milestone work) go to the **integration
  branch**: `dev`, unless CLAUDE.md records another with an
  `Integration branch: <name>` line (e.g. `Integration branch: main`,
  typical for a team project whose mainline predates this workflow).
- **Branch check (before any commit).** If the current branch is not the
  integration branch:
  - It is `dev` and doesn't exist yet: create it from the current branch
    (`git checkout -b dev`), tell the user, and continue. It has no
    upstream, so its first push is `git push -u origin dev`.
  - Otherwise (it exists but another branch is checked out, or a recorded
    non-`dev` branch doesn't exist): show the user and ask before
    switching or creating anything; commit nothing until it is resolved.

## Push

CLAUDE.md records whether workflow commits go to the remote:

- `Push: yes` — skills push their commits as each skill says, under "Git
  safety".
- `Push: no` — commits stay in the local repository. Every `git push`
  step in these skills is skipped, and so is everything that exists only
  for the remote: the `git pull --rebase` before it, `@{u}` checks, `-u`,
  and pull requests. The checkpoint check still runs (with no upstream it
  inspects every commit): a commit on top of a `wip(` checkpoint would
  break `/close-milestone`'s squash. The commit mode is always `direct`. Where a skill checks the remote for a branch
  (`git ls-remote`), check the local one (`git rev-parse --verify`)
  instead. `supabase db push` is not a git push and is unaffected.

**Asking.** `/app-overview` asks at the start of the project; any other
skill that is about to push asks if the line is missing (projects started
before the line existed). Ask: "Should the workflow's commits be pushed
to the remote, or stay local only?" Push is the default; offer local
first when `git remote` lists nothing, and mention that pushing needs a
remote. Record the answer in CLAUDE.md so no later session asks again.
To switch later, the user edits the line; the first push after switching
to `yes` sets the upstream with `-u`.

## Commit mode

CLAUDE.md records how milestone work reaches the integration branch and
`main`:

- `Commit mode: direct` — `/close-milestone` commits and pushes to the
  integration branch, and merges it into `main` when the last milestone
  closes.
- `Commit mode: pr` — each milestone closes through a pull request to the
  integration branch, and the final update through a PR to `main`. The
  skills open the PRs and never merge them; the user merges on GitHub.

**Asking.** Under `Push: no`, don't ask: record `Commit mode: direct`.
Otherwise `/plan-milestones` asks during its questions phase;
`/close-milestone` asks if the line is missing (projects planned before
the line existed). Ask: "Close milestones by pushing directly, or through
pull requests?" and explain in one or two sentences: PR mode is
recommended for team work, when someone else reviews the code, or when
the repo protects the integration branch or `main`; direct is simpler and
faster for a solo project. Record the answer in CLAUDE.md so no later
session asks again.

## Keeping the machine awake

A sleeping machine cuts off every running agent mid-response; each one
resumes minutes later, and a group loses hours. On macOS (`uname` prints
`Darwin`), `/next-milestone` and `/next-group` start this once their
preflight passes, and again whenever work resumes after the user's
feedback:

```
nohup caffeinate -is -t 28800 >/dev/null 2>&1 & echo $! > .git/milestone-loop-awake.pid
```

They stop it whenever they hand over to the user or write a handoff:

```
kill "$(cat .git/milestone-loop-awake.pid)" 2>/dev/null; rm -f .git/milestone-loop-awake.pid
```

The 8-hour limit ends it if a session dies. `-s` holds only on AC power:
on battery a closed lid still sleeps the machine. Other systems: skip.

## Grill-me

`/grill-me` is a third-party skill (`mattpocock/skills`) that
`/app-overview` and `/plan-milestones` suggest for their optional grill
pass. The workflow never depends on it.

When a skill suggests the grill pass and `/grill-me` is not among the
available skills, ask: "`/grill-me` isn't installed. Install it now?"
(once per session). On yes, run:

```
npx -y skills add mattpocock/skills --skill grill-me --global --agent claude-code --yes
```

A Node version warning from `npx skills` is harmless unless the command
fails. If `/grill-me` still isn't available afterwards, tell the user it
loads in their next session. On no, or if the install fails, move on
without the grill pass.

Never copy grill-me into this plugin: installing from source keeps its
updates and attribution.

## Git safety

Under `Push: no`, the rules below about pushing, pulling and the remote
don't apply (see the "Push" section); the rest do.

- Never use `--force` on push.
- Never amend or rewrite commits from previous milestones, or anything
  already pushed. Rewrites of local, unpushed commits are allowed only
  for: the `git pull --rebase` below; `/close-milestone`'s soft-reset
  squash of the current milestone's `wip(M-XX)` commits, or its split of a
  group's `wip` commits into one commit per member; and discarding the
  `wip` commits of a milestone or group the user abandons.
- `wip(M-XX)` and `wip(group)` commits, `wip/M-XX` branches and the
  `.worktrees/` folder are local only: never push one. `/close-milestone`
  squashes or splits the commits away before its push.
- **Checkpoint check.** A skill other than `/close-milestone` that
  pushes checks first, before any other work: if a local-only commit
  (`git log @{u}..HEAD --oneline`; with no upstream, every commit) is a
  `wip(` commit, a milestone or group is mid-flight and the push would
  publish it. Stop, and tell the user to run the skill after that work
  closes.
- Within a closed group, only the last `M-XX` commit is guaranteed to
  build: the members were built and tested together, and a file two
  members changed lands in the later one's commit.
- Never commit to `main` unless it is the integration branch. Otherwise
  `main` changes only at project completion, through `/close-milestone`,
  with the user's explicit yes.
- Before every push, `git pull --rebase` from the integration branch to fold
  in anything pushed meanwhile (another session or an automated job). Skip
  the pull only on a branch with no upstream yet. On a rebase conflict,
  `git rebase --abort`, report the conflicting files, and stop — never
  resolve it blindly.
- If the push fails (diverged remote, permissions), report and stop — no
  recovery attempts without the user.
