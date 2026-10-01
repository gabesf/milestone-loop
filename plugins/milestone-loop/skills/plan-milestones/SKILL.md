---
name: plan-milestones
description: Step 2 of the milestone-loop workflow. After the approver signs
  off on the overview, generates the implementation guidance docs — CLAUDE.md updates,
  milestones plan, initial decision records, and cross-referenced system/
  concept/guideline docs.
disable-model-invocation: true
---

# Milestone planning

Turn the approved application overview into the documents that will guide an
agent through implementation. This is the phase where the user works the most:
ask as many questions as needed. A bad plan here costs every milestone later.

## Preflight

1. `docs/overview.md` must exist. If not, stop and point the user to
   `/app-overview`.
2. Read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it.
3. Ask explicitly: "Has the approver signed off on the overview?" Do not
   proceed without a yes. This is a human gate, not a formality — on a
   solo project too (conventions, "Approver").
4. Check whether the project is a git repository. Not mandatory — but if it
   isn't, warn the user that the plan won't be committed/pushed at closing
   and that milestone work won't be versioned, then continue normally.
5. Load the stack reference as the conventions' "Stack reference" section
   says and apply its section for this skill before proceeding. (This
   skill writes the `Stack:` line; if it is missing, settle the stack with
   the user first — every stack the project mixes, e.g. a machine with a
   controller is `mechanical, electronics`.)

## Process

1. Read the overview and the repo's CLAUDE.md (house patterns, engine/stack
   rules, folder conventions).
2. Scan the rest of `docs/` for pre-existing material (briefs, specs, and
   especially images — `docs/references/` holds the reference images
   collected by `/app-overview`, and there may be more elsewhere). Actually
   look at the images, don't just list filenames; they are the main visual
   input for planning.
   - On conflict with the overview, the overview wins — it's the approved
     document. If it's genuinely unclear whether something conflicts or
     complements, ask the user instead of deciding silently.
   - Link useful material from the docs generated below (a milestone's Docs
     line, a system/concept doc, or a decision's Context) so implementing
     agents find it — e.g. a UI mockup linked from the milestone that builds
     that screen.
3. Ask questions before generating. Typical areas: technical choices left
   open, content/asset availability and who produces it, priority order among
   requirements, risky or uncertain features, what "done" means for the
   trickiest requirements. Batch and iterate.
   - Ask the stack-specific questions from the stack reference's
     plan-milestones section, if one exists (see Preflight).
   - Ask the model-tier questions: which model each tier maps to, and may
     the top tier be used for engine milestones or should this project cap
     at the standard tier? (Details in "Model tier per milestone" under the
     docs/milestones.md output.)
   - Ask the review-policy questions: (a) run the adversarial review gate
     on which milestones — all (recommended), only the ones the plan tags
     as critical, or none? (b) schedule cumulative audit checkpoints at key
     points — yes or no? (Details in "Review policy" under the
     docs/milestones.md output.)
   - Ask the commit-mode question: close milestones by pushing directly,
     or through pull requests? (Wording, and when PR mode is recommended,
     in the conventions' "Commit mode" section; skipped under `Push: no`.)
   - If the project has visual content, always ask explicitly whether final
     art assets are available or placeholders will be used. If placeholders:
     record it in CLAUDE.md, and account for the swap in the plan (which
     milestones integrate final art, and note in Notes any milestone whose
     acceptance criteria depend on assets that don't exist yet).
4. Generate the documents below. Beyond them, create topic docs (§4) only
   under the rules stated there — keep things simple, don't overengineer.
   Add whatever docs, milestones and CLAUDE.md rules the stack reference's
   plan-milestones section specifies (e.g. a runtime control panel).
5. Present everything and iterate on feedback.
6. **Grill pass (optional, encouraged).** Before committing, suggest the user
   run `/grill-me` over the generated plan. Explicitly tell them it is
   optional but encouraged. If `/grill-me` is not installed, offer to
   install it (conventions' "Grill-me" section). Unlike the overview grilling,
   the target here is mostly the developer themself: technical choices, milestone sizing,
   feasibility, acceptance criteria. Questions the dev can't answer should be
   resolved before the commit — most by the dev digging into the problem, but
   the dev can take product-side questions directly to the approver.
7. Commit (see Closing).

## Outputs

### 1. CLAUDE.md (update, don't replace)

Add a project-specific section: what this project is (one paragraph), a
`Stack: <stack>` line naming the project's stack (e.g. `Stack: unity`), or
its stacks comma-separated when it mixes them (e.g. `Stack: mechanical,
electronics`; conventions' "Stack reference") —
this is what lets every later workflow skill find the stack reference — key
technical decisions (including pinned engine/tooling versions, if
applicable), where the entry scene / main code lives, anything an
implementing agent must know that isn't in the base CLAUDE.md. Keep the
existing base content intact. If milestone work integrates on a branch
other than `dev`, record it with an `Integration branch:` line (see the
conventions' "Integration branch" section). Record the model-tier lines
settled in the questions phase (see the conventions' "Model tiers"
section) and the `Commit mode:` line (see the conventions' "Commit mode"
section).

End the section with a **doc index**: a linked list of every file under
`docs/systems/`, `docs/concepts/` and `docs/guidelines/` with a one-line
description each, so an implementing agent knows what exists and reads only
what its milestone needs.

### 2. docs/milestones.md

Header: a summary table (ID | Title | Status | Covers). Then one section
per milestone, labels exactly as below (conventions, "Language and
labels"):

## M-01: [title]
- **Status:** open            (open | in-progress | done)
- **Covers:** R-01, R-03
- **Acceptance criteria:** written NOW, before implementation; short,
  verifiable statements of what must be observably true.
- **Notes:** dependencies on other milestones, risks, anything relevant.
- **Docs:** relative links to the `docs/systems|concepts|guidelines` files
  this milestone touches — the implementing agent reads these first.

Sizing rules — these matter more than elegance:
- One milestone = implementable in one agent session (one context window)
  AND manually testable by the user in under ~20 minutes.
- Every milestone must end in something the user can actually test. If a
  milestone would end in invisible plumbing, merge it forward or add a
  minimal visible probe to its acceptance criteria.
- First milestone should produce a running skeleton, however small.
- Apply the sizing/first-milestone rules from the stack reference's
  plan-milestones section, if one exists (see Preflight).

Coverage check: every R-ID from the overview must appear in at least one
milestone's "Covers". After generating, verify and report any uncovered
requirement to the user explicitly — uncovered requirements are plan bugs.

**Review policy — the user decides both knobs.** During the questions
phase, ask explicitly:

- **Per-milestone adversarial gate** (the review in `/next-milestone`):
  run it on **all milestones (recommended** — the gate is where most bugs
  die before the user ever tests**)**, only on milestones the plan tags as
  critical, or not at all?
- **Cumulative audit checkpoints** (below): schedule them at key points —
  yes or no?

Record the gate answer in CLAUDE.md as `Review gate: all`, `Review gate:
tagged` (only critical) or `Review gate: none` — these English values
exactly — so `/next-milestone` sessions honor it without re-asking.
Checkpoints live in the milestones' Notes (below). Under `tagged`, tag
the chosen milestones' Notes with `Adversarial gate: yes` — typically the
engine/algorithm milestones plus anything a checkpoint below would
guard. Under `none`, the plan
carries no review machinery: note once that the user is trading review
coverage for speed/cost, then respect the choice without re-litigating it.
If the user declines the checkpoints, skip the section below entirely.

**Audit checkpoints (only if the user opted in).** Each milestone already
gets an adversarial review of its own diff (the gate in `/next-milestone`,
per the policy above), but that gate never sees the ACCUMULATED codebase —
duplication between milestones, drift, security posture as the surface
grows. While generating the plan, identify the few milestones where a
broader cumulative audit is worth its cost, and schedule it in that
milestone's Notes (what to audit, which lenses, and that findings are
handled before that milestone's own work ships). Typical triggers — apply
the ones that exist in this project, don't invent checkpoints for the sake
of it:

- **Before first public exposure** (deploy, release build, store submission,
  playtest with external users): security-focused pass — auth on every
  route/endpoint, access policies per table, secrets in the client bundle,
  exposed cron/webhook endpoints.
- **Before an irreversible or high-volume operation** (bulk data migration,
  save-format change, economy reset): correctness pass focused on the
  engines that operation will stress — a bug found mid-migration
  contaminates the operation's own acceptance criteria.
- **At project completion** (last milestone, before `main` is updated): one
  full pass — leftovers, duplication, security — the last cheap chance to
  fix the accumulated whole before real users depend on it.

Two to three checkpoints is the healthy number for a full plan. More than
that re-reviews what the per-milestone gate already covers and mostly
resurfaces dismissed findings.

**Model tier per milestone.** Session model is the workflow's main cost
lever, so the plan should set expectations up front. Tag each milestone's
Notes with `Tier: top` for milestones whose core is an engine/algorithm
with subtle invariants (reconciliation, migration, simulation) and
`Tier: standard` for conventional milestones (screens, CRUD, reports,
integrations). The tiers, the CLAUDE.md lines and their defaults are
defined in the conventions' "Model tiers" section. This planning session
is itself top-tier work: a planning error costs every later milestone.
`/close-milestone` needs no tag: it normally runs in the same session as
`/next-milestone`.
**Mapping and ceiling — ask the user.** During the questions phase, show
the default mapping and ask which model each tier should use (lineups and
plan access change), and whether the top tier may be used for the engine
milestones or the project should cap at the standard tier. The top tier is
the scarce resource (on quota plans, its quota is typically the only one
that runs short), so this is the user's budget call, not the planner's — do
not assume either answer. Record `Model tiers:` in CLAUDE.md, plus
`Model cap: standard` if chosen and `Model floor:` if the user wants one
other than the default. Under a cap, still tag engine milestones
`Tier: top` — the cap lowers them at session time and the tag keeps
driving TDD below.

**TDD for engine milestones.** The same milestones whose core is an
engine/algorithm (the ones tagged `Tier: top` above) must
also be tagged `TDD: yes` in their Notes. This tells `/next-milestone` to
enforce red-green TDD — a failing test before the code for each engine
behavior — instead of the default "write cheap automated checks" policy.
The tag is set here at planning time, not decided per-session.

**Parallel groups.** Once the milestones are drafted, read
`../find-parallel/SKILL.md` and apply its Analysis section to the whole
plan (footprints come from the criteria and docs: there is little or no
code yet), then tag the groups as its Record section's steps 2–3 say. A
group lets `/next-group` implement its members at the same time and costs
the user one test session instead of one per milestone. Present the groups
with the plan; the user may reject any of them.

### 3. docs/decisions/

One file per decision already made during this planning session, ADR-style:
`NNNN-short-title.md` with sections Context / Decision / Consequences.
Number from 0001. Only real decisions (things that could have gone another
way), not restatements of requirements. When a decision shapes a system or
guideline, link to its doc (§4) — and that doc links back to the decision.

### 4. docs/systems/, docs/concepts/, docs/guidelines/

Topic docs that carry durable knowledge across milestone sessions:

- **`docs/systems/`** — one file per major system of the project (e.g.
  `input.md`, `save-load.md`, `scoring.md`): responsibility, public surface,
  how it connects to other systems, constraints an implementer must respect.
- **`docs/concepts/`** — one file per domain concept that needs a stable,
  shared definition (game rules, entities, states) so milestones don't drift
  on what a term means.
- **`docs/guidelines/`** — cross-cutting rules that apply to many milestones
  (e.g. UI conventions, asset naming, testing approach) and don't belong in
  CLAUDE.md's base content.

Rules — these prevent the doc set from rotting:

- Create a doc only when **more than one** milestone or decision will consult
  it. Knowledge used by a single milestone belongs in that milestone's notes.
- Every doc must be **referenced from at least one other file** (CLAUDE.md
  index, a milestone's Docs line, or a decision). An unreferenced doc is a
  plan bug — same severity as an uncovered requirement.
- Cross-reference with relative markdown links, in both directions where the
  relationship matters (decision ↔ system doc, milestone → concept doc).
- Keep each doc short and stable: what an implementing agent must know, not
  a design essay. Prefer updating an existing doc over creating a new one.

Reference check: after generating, walk every file under `docs/` and verify
(a) every topic doc is linked from somewhere, and (b) every link resolves.
Report violations to the user explicitly.

## Closing

When the user approves the plan: commit everything on the integration
branch with message `docs: milestone plan` and push (unless `Push: no`),
under the conventions' "Integration branch", "Push" and "Git safety"
sections. If the
project is not a git repository, skip commit/push and remind the user to
set one up before the milestone loop.
Tell the user the loop starts with `/next-milestone` in a fresh session
(`/clear` first), and that tagged groups run with `/next-group` when their
turn comes.
