---
name: physical-build
description: >-
  Shared reference for physical-project stacks in the milestone-loop
  workflow. NOT an invocable skill and not a stack of its own — the
  physical stack references (stack-mechanical, stack-electronics) name it,
  and the generic workflow skills load it with them. Holds what every
  physical project shares: design vs build milestones, hazards, failsafe
  ordering, measured dimensions, the bill of materials and the as-built
  record. Each section below maps to one workflow skill.
disable-model-invocation: true
---

# Physical build reference

Rules every physical project shares, whatever its disciplines. The stack
references that name this document add their own rules on top; sections
are applied like a stack reference's (conventions, "Stack reference").

A physical project differs from software in three ways these rules
handle: making a thing takes days or weeks and often a supplier, so most
of the time is spent between milestones; the agent can verify a model or
drive a bench rig but cannot build, install or measure the object; and a
bug can hurt a person or kill a living being.

## Milestone kinds

Every milestone is tagged in its Notes with `Kind: design` or
`Kind: build` (fixed English labels).

- **`Kind: design`** — the agent's work: models, scripts, firmware,
  drawings, fabrication files. It may use hardware already in hand on the
  bench (flash a board, read a sensor) — whatever the stack references'
  `next-milestone / agent-executed testing` sections list. Ends in a
  **verified package**: everything the agent can check has passed, and
  the user has reviewed the previews.
- **`Kind: build`** — the user's work: fabricate, assemble, wire, install,
  then test the real object. Its acceptance criteria are observations and
  measurements on the object, each with an expected value and a
  tolerance. It ends with the as-built record (`docs/as-built/M-XX.md`).
  The agent's own work in it is small: a measurement sheet, a jig or
  template, a config change.

Any milestone that needs physical items (a board on the bench, parts to
assemble) lists them in a `Parts:` line in its Notes. Waiting for parts,
a supplier or a free workshop day happens **between** milestones, never
before one starts: a milestone with a `Parts:` line starts only once
everything on it is in hand. One active unit at a time still holds.

## plan-milestones

- **Questions (add to the questions phase):**
  - What can hurt someone? Moving parts, mains voltage, stored energy
    (springs, pressure, batteries), heat, thrown material.
  - Does the project keep living beings (animals, plants, fish) or run
    unattended? If yes, list what a failure would cost and how fast
    (e.g. no aeration kills fish in hours).
  - Is this a new object, or a change to one that already exists? An
    existing object is measured before it is modelled.
- **Tag every milestone** `Kind: design` or `Kind: build`, and give it a
  `Parts:` line when it needs physical items, with the slow ones
  (supplier lead time) marked. A build milestone names in its Notes the
  design milestone(s) whose package it builds (a dependency).
- **Sizing.** A design milestone: one agent session, reviewable by the
  user in under ~20 minutes. A build milestone: at most one workshop day,
  then a test of at most ~20 minutes. Bigger means split.
- **First milestones.** Each physical stack reference states its own
  first milestone. With several, each is that stack's first milestone,
  not the plan's: the mechanical one comes first (the object and its
  frame), the electronics one next.
- **Failsafe first.** When something can be harmed — a living being, a
  person, the machine itself — the milestones that detect the failure and
  move to a safe state (alarm, backup, guard, cut-off) come BEFORE any
  milestone that automates the thing that can fail. A heater controller
  does not ship before the over-temperature cut-off and alarm do.
- **Bill of materials.** Create `docs/bom.md`: one table (Part | Qty |
  Spec | Source | Status: `needed`, `ordered`, `in hand`, `used`), linked
  from the CLAUDE.md doc index. Milestones add to it; every `Parts:` entry
  must appear in it.
- **CLAUDE.md:** record the workshop and the measuring tools the user
  has (caliper, multimeter, scale…) — acceptance criteria may only ask
  for measurements those tools can take.

## next-milestone / bootstrap

- **Parts check.** For a milestone with a `Parts:` line, ask before
  planning whether every item on it is in hand. If not, stop: leave it
  `open`, list the `open` milestones that don't depend on it, let the user
  pick one, then re-run Preflight 2 for the picked milestone. Never start
  on a promise of parts.
- **`Kind: build` with no agent work.** When the milestone needs no
  model, file or firmware change, skip the implementer and the review
  gate (there is no diff) and go straight to the testing doc.

## next-milestone / quality gates

- **Dimension provenance.** Every dimension that decides a fit, a
  clearance or a rating is one of: *measured* (on the real object, by the
  user), *datasheet* (cite it), or *modelled* (our own design value).
  Record the source next to the value (script comment, systems doc). A
  measured value beats a modelled one, always. Never invent the dimension
  of something that already exists — ask the user to measure it, and say
  with which tool.
- **Re-check the neighbours.** A change to one part re-checks every part
  it touches (fits, clearances, bolts, wiring, connectors), not just the
  part itself.
- **Prefer what can be bought locally.** Standard sizes and standard
  hardware the user can actually buy over custom or imported parts;
  update `docs/bom.md` for anything added or changed.

## next-milestone / agent-executed testing

- `Kind: design`: everything the stack references list.
- `Kind: build`: tier 1 is empty at hand-over — the object exists only
  once the user has built it. Say so under "Verified by the agent". The
  agent's checks (each reported measurement against its expected value
  and tolerance, every photo looked at) run during feedback triage and
  are recorded there.

## next-milestone / testing doc

- **Hazards** (every milestone, never omitted): what can hurt during this
  test and what is done first — guard on, power isolated, lockout,
  protective equipment, a second person present. A design milestone whose
  review hurts no one says "None — review only".
- **`Kind: build` adds:**
  - **Build steps** — fabrication and assembly in order, each with the
    file or drawing it uses. Not counted in tier 2's ~5-step budget: tier
    2 ("How to test") starts once the object is built.
  - **Measurements** — table: What | Expected | Tolerance | Measured |
    Tool. Measuring is ONE tier-2 step, however many rows. The user
    reports values in chat; the agent fills the Measured column.
  - In the hand-over, ask the user to put photos of the finished object,
    and of any spot that came out different from the drawing, in
    `docs/as-built/img/` (or to give their file paths).
- **`Kind: build` hand-over handoff.** The build can take a workshop day,
  so the session that hands over rarely closes. At hand-over write
  `docs/handoff/M-XX.md` (or update it) with Next step "feedback triage:
  record the user's measurements and photos". A later session resumes
  there through Preflight 3.

## next-milestone / feedback triage

For `Kind: build`, the user's comments are measurements, photos and
observations. Record each reported value in the testing doc's Measured
column as it arrives, compare it with its tolerance, then for each
deviation:

- **Inside tolerance** → record it for the as-built record.
- **Outside tolerance, still works** → record it. If the part is an
  interface other parts fit to, update the model or script to the
  measured value (a delegated fix) so the next design starts from the
  real object. A fabrication error in a part is recorded, not designed
  in: the next copy is made to the drawing.
- **Doesn't work** → the milestone closes anyway, with the failure in its
  Deviations and its as-built record; the fix (a design milestone, and a
  new build milestone) goes in through `/replan`, with a decision record.
  A failed build never stays `in-progress` blocking the queue.

## find-parallel

- `Kind: build` milestones run alone and get no group tag: they are
  sequential workshop work, not code to merge.

## close-milestone

- **`Kind: build`: as-built record (before committing).** Write
  `docs/as-built/M-XX.md`: date, the measurements table with every value
  filled (or "not measured" and why), the deviations and what was done
  about each, and links to the photos in `docs/as-built/img/` (resize
  them to about 1600 px on the long side so the repository stays small).
  A build milestone does not close without it. Update `docs/bom.md`
  statuses (`in hand` → `used`).
- **Model follows the object.** Any outside-tolerance interface value not
  yet in the model is either fixed now or listed in the Notes of the next
  design milestone that touches that part — never left only in the
  as-built record.
