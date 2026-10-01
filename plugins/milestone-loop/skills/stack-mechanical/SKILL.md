---
name: stack-mechanical
description: >-
  Mechanical stack reference (machines, structures, sheet metal, 3D-printed
  parts; CAD in FreeCAD through its MCP server; FEM and MuJoCo
  simulation) for the milestone-loop
  workflow. NOT an invocable skill — the generic workflow skills read this
  document via a relative path when the project's CLAUDE.md lists
  `mechanical` in its `Stack:` line. Each section below maps to one
  workflow skill.
disable-model-invocation: true
---

# Mechanical stack reference

Stack-specific rules for mechanical projects, consumed by the generic
workflow skills. Each section is applied by the skill it is named after,
at the point its preflight says to read this document. Rules here have the
same force as the invoking skill's own rules.

**Also load `physical-build`** (`../physical-build/SKILL.md`, or by name)
and apply its sections the same way. It holds the design/build milestone
kinds, hazards, measured dimensions, the BOM and the as-built record.

## plan-milestones

- **CAD tool.** Default: FreeCAD driven through the FreeCAD MCP server.
  Ask, and record the tool (and FreeCAD version) in CLAUDE.md.
- **Fabrication question (mandatory).** Ask which processes the user has
  in hand or buys outside, with their limits: laser/plasma cutting (max
  thickness), press brake (max length and thickness), welding (process),
  3D printer (volume, materials), lathe/mill, hand tools only. Also: does
  the user prefer fewer welds, fewer parts, or the lowest cost? Record a
  `Fabrication:` line in CLAUDE.md (e.g. `Fabrication: laser ≤ 6 mm
  outsourced, press brake ≤ 1000 mm, MIG welding, FDM 250 mm`). Designs
  use only these processes.
- **Materials.** Ask which stock (sheet thicknesses, tubes, bars) the
  user can buy locally and record it; designs use stock sizes only.
- **Reference frame.** Record in CLAUDE.md how the model's axes map to
  the real object (which way is up, front, the operator's side) and which
  named view shows what — a frame nobody wrote down sends the agent's
  renders and the user's words in different directions.
- **Folders.** Record in CLAUDE.md where things live, defaulting to:
  the CAD document(s) at the root, `scripts/` for geometry scripts,
  `images/NN_<step>/` for each design step's previews and option sheets,
  `sim/` for simulation scripts, `fabrication/` for the released package
  (drawings, DXF, STEP, a README).
- **First milestone.** Changing an existing object: an as-built model of
  what exists (imported STEP or modelled from the user's measurements),
  checked against photos — every later design starts from it. A new
  object: a skeleton assembly with the envelope, the fixed interfaces
  (mounting points, shafts, openings) and the reference frame.
- **One decision per step.** The user designs with the agent, not after
  it. Plan design milestones around decisions the user makes (an opening,
  a joint, a part), and never pre-decide geometry the user hasn't seen.
  Where a step has real alternatives, its criteria include an **options
  sheet**: 2–4 options drawn side by side with their numbers (area, mass,
  clearances), for the user to pick.
- **Simulation question.** Ask which risks a simulation should answer
  before metal is cut, and pick the tool by the question:
  - *Does the part hold, how much does it deflect?* → FEM in FreeCAD
    (CalculiX), run through the MCP.
  - *How does the mechanism move, what forces and collisions over time?*
    (feeders, linkages, splitters, rotors) → MuJoCo from Python scripts.
  - Anything else (granular flow, fluids, heat) → say what tool it would
    need and ask; a hand calculation or a simple Python model is often
    enough.
  A simulation goes in a design milestone's criteria as the question it
  answers and its pass threshold (e.g. "stress ≤ 0.5 × yield under the
  jam load"). Record the tools in CLAUDE.md, and for MuJoCo the exact
  Python command (e.g. `~/.venvs/sim/bin/python`) — the `python` on PATH
  is often another interpreter. Never plan a simulation nobody will act
  on. A milestone with a simulation criterion is not an engine milestone:
  no `TDD: yes` for it — the validation case below plays that role.

## next-milestone / bootstrap

- **Toolchain-alive check (mandatory before any CAD work).** Load the
  FreeCAD MCP tools (via ToolSearch if deferred) and make one cheap
  read-only call (e.g. RPC status or list documents). If the tools are
  absent or the call fails, stop and tell the user to open FreeCAD with
  the MCP add-on's RPC server running, then re-invoke the skill. Never
  fall back to editing the `.FCStd` archive by hand.
- **.gitignore.** Ensure it holds `*.FCBak` and `*.FCStd1` (FreeCAD
  backups); the `.FCStd` document itself is committed.
- **Simulation toolchain (only when this milestone simulates).** FEM:
  through the MCP's code-execution tool, run `from femsolver import
  settings; print(settings.get_binary("Calculix"))` and confirm a mesher
  (Gmsh or Netgen) is available to FreeCAD. MuJoCo: run the recorded
  Python command with `-c "import mujoco; print(mujoco.__version__)"`.
  If any fails, stop and tell the user what to install.

## next-milestone / quality gates

- **Scripts are the source of truth.** Every part and assembly change is
  made by a re-runnable script in `scripts/`, run inside FreeCAD through
  the MCP, that rebuilds its objects from named parameters at the top
  (each with its provenance — `physical-build`). Running it twice gives
  the same model. Never hand-tweak an object without changing its script.
- **Design for the recorded fabrication.** Only processes in the
  `Fabrication:` line; only stock sizes (a non-stock thickness becomes
  stock plus shims, not a special order). Sheet metal states its inner
  bend radius and K-factor, has bend reliefs, and its flat pattern is
  generated by the script, not drawn. Welds are reachable by the torch;
  parts locate each other (tabs, slots, spigots) instead of relying on
  hand alignment.
- **Standard hardware** by designation (ISO/DIN/ASTM), with tool access
  checked: a wrench or socket fits and swings, a nut has room to turn,
  the assembly order is possible.
- **Interference and clearance after every change.** Check the whole
  assembly for collisions (report every overlapping pair and its volume)
  and report the clearances that matter (moving parts, nuts, fits) as
  numbers. Zero unexplained collisions before proceeding.
- **Moving parts.** Rotating parts: mass, centre of mass offset and the
  balance tolerance. Openings near moving parts: reach distance against
  ISO 13857 (or the local equivalent), or a guard in the plan.
- **Only what the user agreed.** Model the decision this milestone covers,
  nothing ahead of it. A new option to show is an options sheet, not a
  model change.
- **Fabrication files only after preview approval.** Drawings, DXF and
  STEP are generated by scripts from the model, and only once the user
  has approved the previews. DXF layers: `CUT`, `BEND`, `ENGRAVE`; state
  which face the DXF shows. Every drawing carries units, scale, material,
  thickness and quantity.
- **Simulations.**
  - One question per simulation, stated at the top of its script with
    the pass threshold.
  - Scripts live in `sim/`, re-runnable, and take their geometry from the
    model by script, never redrawn by hand.
  - **FEM:** the script builds its analysis (mesh, material, supports,
    loads) in its own FreeCAD document, never in the committed model,
    solves through the MCP's `run_fem_analysis`, and reads the
    thresholded value from the result object.
  - **MuJoCo:** the script writes the MJCF itself from the model —
    FreeCAD has no MJCF exporter. Meshes in metres (FreeCAD works in
    mm). MuJoCo collides a mesh as its convex hull, so non-convex parts
    that collide (blades, hoppers, rotors) are split into convex pieces
    or replaced by primitives sized from the model.
  - **Provenance** of every input, as `physical-build` requires for
    dimensions, plus two kinds for simulation: *estimated* (loads,
    friction — say how: hand calculation, a reference, a margin) and
    *numerical* (mesh size, time step — from the convergence check).
  - **Validate before trusting:** a validation case with the same
    supports, load application and material as the real run, on a
    simplified geometry with a hand answer (a beam formula, a free fall,
    a known speed), must agree within a tolerance stated in the script
    (default 10 %). Until it does, the result is reported as
    unvalidated.
  - **Convergence (always):** run at two resolutions — FEM element size
    halved, MuJoCo time step halved — and report both; more than 5 %
    apart on the thresholded quantity means not converged. FEM: judge
    stress away from supports and sharp corners (or use deflection); a
    peak there that keeps rising with refinement is a singularity,
    reported as such, not a result. MuJoCo: threshold impulses or
    time-averaged forces, never single-step contact peaks.
  - Results are numbers against the threshold, plus plots and key frames
    (start, worst case, end) saved under `images/NN_<step>/`. A
    simulation never replaces a build milestone's measurement.
- **One implementer drives FreeCAD at a time.** There is one instance
  and one document; never run implementers on the model in parallel.
- **FreeCAD visibility.** Making a group visible also shows all its
  children. Before saving, read each top-level object's visibility
  through the MCP and match it to what the user expects to see when
  they open the file.

## next-milestone / agent-executed testing

Tier-1 steps the agent drives itself through the FreeCAD MCP:

- Re-run the milestone's scripts and confirm the model is unchanged.
- The interference check and clearance report from the quality gates.
- Mass, volume, centre of mass where they matter.
- Renders from the recorded named views and section views — look at every
  image produced before handing it over.
- Regenerate flat patterns and DXF, then re-read them: closed contours,
  right layers, right size.
- Re-run the milestone's simulations, their validation cases and both
  convergence resolutions; look at every plot and key frame.
- Prerequisite to ask the user for, if missing: FreeCAD open with the MCP
  add-on running.

## next-milestone / testing doc

- **Previews to review:** each image or drawing path with what to check
  in it (fit, look, can it be built in this workshop). This is tier 2 for
  a design milestone: judging whether it makes sense and can be made.
- **Simulation results:** per simulation, the question, the answer
  against its threshold, the validation case and its error, and the
  convergence pair. Checking the *estimated* inputs (loads, friction) is
  ONE tier-2 step, reproduced in the hand-over: they are the user's
  knowledge of the machine, not the agent's.

## find-parallel

- **Hotspots:** the CAD document (`*.FCStd`), shared geometry modules in
  `scripts/`, shared simulation modules in `sim/` (MJCF writer, materials
  table), `docs/bom.md`.

## next-group

- **Group mode: serial.** There is one FreeCAD instance and one document;
  members are implemented one after another in the main tree.

## close-milestone

- **Stale fabrication files (before committing).** If the milestone
  changed a part that `fabrication/` contains, regenerate that part's
  files from the scripts and include them — a stale DXF gets the wrong
  part cut.
- **Stale simulations.** If the milestone changed a part that a
  committed simulation covers, re-run that simulation and record the new
  result against its threshold — a stale pass must not back a build.
- **Backups.** No `*.FCBak` / `*.FCStd1` in the commit.
