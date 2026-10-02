---
name: find-parallel
description: Finds open milestones in docs/milestones.md that can be
  implemented at the same time (no dependency between them, no overlap in
  the files they touch) and groups them, so /next-group runs each member
  with its own implementer and the user tests the whole group in one
  session. Proposes the groups, records the approved ones as `Group: G-XX`
  tags in the members' Notes, and commits. /plan-milestones applies its
  Analysis while writing a plan; run it directly on existing projects or
  after /replan.
disable-model-invocation: true
---

# Find parallel groups

Find the open milestones that can be implemented at the same time, propose
them as groups, and record the approved groups in docs/milestones.md. A
group costs the user one plan approval, one test session and one close
instead of one of each per milestone. The analysis therefore looks for
two things: members that cannot break each other, and members the user
can test in one sitting.

Token note: this skill reads and reasons but writes only tags. The
standard tier is enough, and a grouping mistake is caught by
`/next-group`, which re-checks a group before running it.

## Preflight

1. `docs/milestones.md` must exist. If not, stop and point the user to
   `/plan-milestones`.
2. Read CLAUDE.md fully, then the `conventions` reference:
   `../conventions/SKILL.md` relative to this skill's base directory, or
   the `conventions` skill by name on hosts that don't state it. Run its
   "Legacy check". Its "Parallel groups" section defines the tag this
   skill writes.
3. Load the stack reference as the conventions' "Stack reference" section
   says; apply its `find-parallel` section during the Analysis.
4. Run the conventions' **checkpoint check** ("Git safety"): this skill
   pushes, so it never runs while a milestone or group is in flight.

## Analysis

`/plan-milestones` also applies this section while it writes a plan. On a
project with no code yet, footprints come from the criteria and docs
alone.

1. **Candidates** are the `open` milestones. These always run alone and
   get no tag:
   - the first milestone of the plan (the running skeleton: everything
     depends on it);
   - a milestone whose Notes schedule an audit checkpoint (the audit needs
     the accumulated codebase);
   - anything the stack reference's `find-parallel` section excludes.
2. **Dependencies.** An M-ID that a milestone's Notes name as a dependency
   ("depends on M-03", "after M-02", or the same in the project's
   Language) is an edge, as in `/replan`. Then look for implicit ones: a
   criterion that uses something another open milestone builds (a screen
   that lists items another milestone creates). Show each implicit
   dependency with its evidence; the user confirms or dismisses it.
3. **Footprint** of each candidate: the files, directories and systems it
   will create or change, predicted from its criteria, its Docs line, the
   systems docs and the current code. On a large codebase, give the code
   scan to one read-only subagent (Explore where the harness has it) with
   the candidates' criteria, and ask for one footprint per milestone, not
   file dumps. Mark the **hotspots**: files most features touch (routing,
   navigation menus, registrations, manifests and lockfiles, shared
   schema) plus the stack reference's list.
4. **Form groups** of two members by default, three at most: the
   orchestrating session's context and the group's manual test budget both
   grow with every member. A group needs:
   - **Independence:** no dependency between members, and every
     dependency of a member `done` or in an earlier group.
   - **Disjoint footprints** (parallel mode). A small additive edit to the
     same hotspot (one route or menu entry each) is a warning, not a
     blocker: `/next-group` resolves it when it merges. Sharing more than
     that (the same component, the core of the same system) is a blocker.
     In serial mode (conventions, "Parallel groups") overlapping
     footprints never block a group.
   - **Preference:** members whose manual tests share a setup (same
     screen, flow or device) and share a tier, and whose combined manual
     test fits one sitting.

   Prefer neighbors in the queue. A group that pulls a later milestone
   ahead of earlier ones changes the priority order: say so explicitly.
5. **Present:**
   - the dependency graph, compact (one line per chain);
   - each group: members, why they are independent (their footprints side
     by side), hotspot warnings, what their manual tests share, and the
     session tier (the highest member tier);
   - the milestones left alone, each with its reason.

   Iterate on the user's feedback. Write nothing before approval.

## Record

1. **Existing tags.** Keep a group whose members are all still `open` and
   that the analysis leaves unchanged, with its G-ID. Remove the `Group:`
   tag from every other `open` milestone. Never touch the tag of a `done`
   or `in-progress` milestone.
2. **New groups** get G-IDs continuing from the highest G-ID anywhere in
   docs/milestones.md and docs/milestones-archive.md, `done` milestones
   included.
3. In each member's Notes, add `Group: G-XX` followed by prose in
   parentheses: its partners, why they are independent, any hotspot
   warning. E.g. `Group: G-02 (with M-05; disjoint: src/profile vs
   src/shop; both add a nav entry).`
4. Commit on the integration branch with message `docs: parallel groups`
   and push (unless `Push: no`), under the conventions' "Integration
   branch", "Push" and "Git safety" sections. Nothing changed: commit nothing.
5. Report the first runnable group (members all `open`, dependencies all
   `done`): its ID, members, tier and that tier's model. Tell the user to
   `/clear`, set `/model`, then run `/next-group`. Do not start it.

## Rules

- Edit only `Group:` tags and their prose in docs/milestones.md, never a
  milestone's status, scope, criteria or position.
- Never start implementing. After committing, stop.
