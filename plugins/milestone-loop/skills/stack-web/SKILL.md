---
name: stack-web
description: >-
  Web stack reference (Supabase + Next.js) for the milestone-loop
  workflow. NOT an invocable skill — the generic workflow skills
  (app-overview, plan-milestones, find-parallel, next-milestone,
  next-group, close-milestone) read this document via a relative path when
  the project's CLAUDE.md lists `web` in its `Stack:` line. Each section
  below maps to one workflow skill.
disable-model-invocation: true
---

# Web stack reference

Stack-specific rules for Supabase + Next.js projects, consumed by the generic
workflow skills. Each section is applied by the skill it is named after, at
the point its preflight says to read this document. Rules here have the same
force as the invoking skill's own rules.

## plan-milestones

- **PWA question.** Ask whether the project is a PWA. If yes, record
  `PWA: yes` in CLAUDE.md — this controls mobile testing rules later.
- **Verification harness (any web front end with visual criteria).**
  Plan it once, in an early milestone, so no milestone pays for it again:
  - a direct entry into every app state a criterion will capture (a URL
    parameter or a test hook, e.g. `?state=game-over`), never playing up
    to the state in real time;
  - one capture command in `scripts/` that opens a state at named
    viewport sizes in a headless browser and writes one downscaled JPEG
    contact sheet, with a port option so parallel members don't collide;
  - raw captures in a git-ignored folder.
  Record the command in CLAUDE.md.
- **DOM test environment.** When the app has UI logic, the test setup
  includes a DOM environment (e.g. happy-dom or jsdom), so a UI behavior
  gets a plain test instead of a hand-built harness.

## next-milestone / bootstrap

- **Supabase CLI check (mandatory before any DB-dependent work).** Verify the
  CLI responds: `npx supabase --version` (or a global `supabase --version`).
  If the project has `supabase/config.toml`, also confirm it's linked
  (`npx supabase projects list` mentions the project, or the link is recorded
  in CLAUDE.md). If the CLI is missing, STOP and tell the user to install it
  before implementation starts — with it, migrations go through `db push` and
  seed/verification data through the CLI, all mechanical; without it, DDL and
  test data become manual SQL Editor work that this workflow is designed to
  avoid.

## next-milestone / quality gates

- **DDL only via `supabase db push`.** Schema changes are always authored as
  SQL migration files under `supabase/migrations/` and applied with
  `supabase db push`. Never use the Supabase Dashboard SQL Editor for DDL —
  it bypasses version control and the migration history, making rollback and
  review impossible.
- **Dry-run migrations in a local Postgres before pushing.** Before running
  `supabase db push` against the remote project, validate the migration
  locally: run `supabase start` (starts the local dev stack including
  Postgres) followed by `supabase db reset` (replays every migration from
  scratch, catching ordering and dependency issues). If the local stack is not
  available (Docker not installed or not running), STOP and tell the user to
  install/start Docker before proceeding — pushing untested migrations to the
  remote project is not acceptable. The remote push happens only after the
  local dry-run succeeds.
- **Captures.** Through the harness, only what a criterion changes, at
  the sizes it names (none named: one default size). One contact sheet
  per milestone goes in the testing doc; raw captures stay in the
  git-ignored folder and are never committed.
- **Mobile testing (PWA projects).** When CLAUDE.md records `PWA: yes`, the
  manual test script (`docs/testing/M-XX.md`) must include a step for
  iOS Safari / PWA testing: open the app on an iPhone (or iOS Simulator in
  Safari), verify layout and touch interactions work. Desktop-only testing is
  not sufficient for PWA projects.

## find-parallel

- **Hotspots:** `supabase/migrations/` (at most one member per group adds
  migrations: they are ordered by timestamp and share one local
  database); `package.json` and the lockfile (at most one member per group
  adds dependencies); the root layout, navigation and middleware.

## next-group

- **Worktree setup:** install dependencies with the project's package
  manager, and copy the untracked env files (`.env`, `.env.local`, …) from
  the main tree into the worktree.
- **Shared resources.** Members work at the same time on one machine, so
  in a worktree: no dev server and no test that binds a port, except the
  preview server and headless browser the harness runs on the port this
  session assigns to that member; only the
  member that adds migrations may use the local Supabase stack
  (`supabase start`, `supabase db reset`, tests against the local
  database); nobody runs `supabase db push`. At the integration check, in
  the main tree and before tier 1: the local migration dry run, then
  `supabase db push`, then the tests that bind a port or need the
  database.
- **Mobile testing (PWA projects):** the group's testing doc gets ONE iOS
  Safari / PWA walkthrough covering every member's screens, as a
  must-have step, not one per member.

## close-milestone

- **Migration file review (before committing).** Inspect migration files under
  `supabase/migrations/` in the diff: check for destructive DDL (`DROP TABLE`,
  `DROP COLUMN`) that isn't guarded by a data migration step, and for
  migrations that assume an empty table when the table may already have rows.
  Flag anything suspicious to the user before committing.
