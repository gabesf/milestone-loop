---
name: stack-unity
description: >-
  Unity stack reference for the milestone-loop workflow. NOT
  an invocable skill — the generic workflow skills (app-overview,
  plan-milestones, find-parallel, next-milestone, next-group,
  close-milestone) read this document via a relative path when the
  project's CLAUDE.md lists `unity` in its `Stack:` line. Each section
  below maps to one workflow skill.
disable-model-invocation: true
---

# Unity stack reference

Stack-specific rules for Unity projects, consumed by the generic workflow
skills. Each section is applied by the skill it is named after, at the point
its preflight says to read this document. Rules here have the same force as
the invoking skill's own rules.

## plan-milestones

- **Unity version question (mandatory).** Always ask which Unity version to
  target — there is no default; offer the editors installed on the machine
  (Unity Hub) as options, but get an answer. Record it in CLAUDE.md.
- **TMP Essential Resources auto-import (first milestone, mandatory).** The
  first milestone's acceptance criteria must include an editor script
  (`[InitializeOnLoad]`, plus a menu item for manual retry) that imports
  `Packages/com.unity.ugui/Package Resources/TMP Essential Resources.unitypackage`
  (pre-Unity-6 fallback: same path under `com.unity.textmeshpro`) whenever
  `Assets/TextMesh Pro/Resources/TMP Settings.asset` is missing. Projects
  created via CLI `-createProject` don't include these resources and
  TextMeshPro renders nothing without them — importing manually via the
  popup is exactly the kind of silent human step this workflow exists to
  eliminate. Write this into M-01's Notes explicitly.
- **Runtime control panel (default: yes).** An in-app panel for tuning
  parameters at runtime, so the user tweaks values during manual testing
  instead of round-tripping every adjustment through a fix cycle. Ask only
  when genuinely unclear (e.g. an editor-only tool). When it applies, wire
  it into the plan:
  - **Systems doc** (`docs/systems/control-panel.md`) specifying: the
    important parameters live in a JSON file; the panel lists them with
    editable controls; it is toggled by ` (backtick) on keyboard platforms
    and by a fallback gesture on touch (e.g. 3-finger triple-tap — the doc
    picks one); edits auto-save; a button restores all defaults, and each
    row has its own reset control ("×") that restores only that
    parameter's authored default and drops its stored override — enabled
    only while the value differs from the default, so a glance shows what
    was touched. The panel ships in ALL builds, including release. The list
    grows every milestone, so it must scroll (wheel/drag plus a scrollbar
    visible on overflow) — a parameter that can't be reached on screen is
    a bug. Panel controls must NEVER hold keyboard focus after the pointer
    releases: the EventSystem keeps the last-touched slider/scrollbar
    selected, so arrow keys (often also gameplay input) silently keep
    driving it — clear the selection on pointer-up for every slider and
    scrollbar the panel builds.
  - **Empty at birth:** the JSON starts with no parameters; each milestone
    registers the tunable values it introduces, never speculated upfront.
  - **Milestones:** an early milestone builds the skeleton (toggle, empty
    list, restore button) — it pairs well with the first running skeleton.
    A milestone expected to introduce tunable values says so in its Notes.
  - **CLAUDE.md rule** in the project section: any tunable value a
    milestone introduces must be registered in the control panel, never
    hard-coded.

- **Proof harness.** When criteria need Play Mode proof (a behavior at a
  point of a level, a measurement over a run), plan once an Editor proof
  harness (e.g. under `Assets/Editor/Proofs/`): jump to a named point
  (seek to the block or wave, spawn the state) instead of playing up to
  it; run faster where physics allows (`Time.timeScale` with a fixed
  timestep); log the values the criteria measure; capture the Game view
  at a named resolution into one contact sheet. One command runs a proof,
  for the implementer and the orchestrator alike.
- **An Editor for the agents (ask once).** By default agents share the
  user's Editor, so the user's Play session or a modal dialog blocks
  them. Ask whether agents get their own Editor (a clone of the project,
  e.g. with ParrelSync, with its own bridge port) and record `Agent
  editor: <path>` or `Agent editor: none` in CLAUDE.md.

## next-milestone / bootstrap

- **Project creation.** When the target milestone creates the Unity project,
  create it via CLI `-createProject` (per the milestone's notes).
- **Toolchain-alive check (mandatory before any Editor-dependent work).**
  Verify the MCP for Unity bridge NOW: load the Unity MCP tools (via
  ToolSearch if deferred) and make one cheap read-only call (e.g.
  editor/project state). If the tools are absent or the call fails, stop and
  tell the user to open the Unity project in the Editor with the MCP for
  Unity bridge running, then re-invoke the skill. Do not fall back to
  hand-editing scenes, prefabs, or other serialized assets — that path is
  forbidden by the quality gates.
  - **Bootstrap exception:** if the Unity project doesn't exist yet (no
    `ProjectSettings/ProjectVersion.txt`) and the target milestone's notes
    say it creates the project, skip the check for now — create the project
    first (CLI `-createProject`), get the Editor open with the bridge
    running (launch it yourself if possible, otherwise ask the user), and
    verify the MCP connection before any Editor-dependent work. Scene/prefab
    work without a verified connection is still forbidden.
- **TMP auto-import before any UI work.** If the project lacks the TMP
  auto-import script described under "plan-milestones", add it before any
  UI work — even if the plan forgot it — and verify the resources actually
  landed.
- **.gitignore (repository root).** Ensure a Unity .gitignore exists at
  the repository root. Beyond the standard entries (`[Ll]ibrary/`, `[Tt]emp/`, `[Oo]bj/`,
  `[Bb]uilds/`, `[Ll]ogs/`, `[Uu]serSettings/`, `*.csproj`, `*.sln`,
  `.vs/`, `.idea/`, `crashlytics-build.properties`, `*.pidb.meta`,
  `sysinfo.txt`, `*.apk`, `*.aab`, `*.unitypackage`), it must also include:
  - `/Assets/_Recovery/` and `/Assets/_Recovery.meta` — crash-recovery
    artifact the Editor drops into Assets; it must never be committed.
  - the generated `config.json` next to the executable, when the project
    uses an external config file.

## next-milestone / quality gates

- Scene and prefab changes only through the MCP tools — never by
  hand-editing serialized files.
- **Proofs** go through the proof harness when the project has one, never
  one-off scripts.
- Always quote asset paths in commands and tool calls — Unity asset paths
  contain spaces (e.g. `"Assets/TextMesh Pro/Resources/TMP Settings.asset"`).
- **Control panel** (the project has one when CLAUDE.md or
  `docs/systems/control-panel.md` says so): register
  every tunable value this milestone introduces, with a sensible default,
  instead of hard-coding it; add nothing for values the milestone doesn't
  touch. Then confirm every parameter is still reachable in the panel — if
  this milestone's additions overflow the layout, fixing the panel is in
  scope.

## next-milestone / agent-executed testing

Tier-1 steps the agent drives itself in Unity projects:

- The MCP for Unity bridge: enter/exit Play Mode, drive scene objects and
  components, read the Console, capture the Game view if the bridge
  exposes it.
- The EditMode/PlayMode test runner and batch-mode CLI runs.
- Prerequisite to ask the user for, if missing: the Editor open with the
  bridge running.
- With an `Agent editor:` path in CLAUDE.md, drive that Editor. Before
  entering Play Mode, check the Editor is not already playing or showing
  a modal dialog; if it is, tell the user in one line at once instead of
  waiting on it.

## next-milestone / testing doc

Only when the project has a control panel (same test as in quality gates):

- Add a **Tunable parameters** section listing each parameter the
  milestone added, with its default and what it affects.
- In the hand-over message, remind the user to open the panel while
  testing (backtick, or the touch gesture from
  `docs/systems/control-panel.md`) — tuning feedback is cheaper live than
  as written comments.

## next-group

- **Group mode: serial.** The project has one Editor and one MCP for Unity
  bridge, and a worktree would be a second Unity project needing its own
  Library import and its own Editor. Members are implemented one after
  another in the main project; the group still gets one plan approval, one
  test session and one close.

## close-milestone

- **Diff inspection for Editor artifacts (before committing).** Inspect the
  diff for Editor artifacts that don't belong to the project — e.g.
  `Assets/_Recovery/` (and its `.meta`) from crash recovery. Remove them and
  add them to .gitignore instead of committing them.
