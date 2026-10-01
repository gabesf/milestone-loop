---
name: stack-electronics
description: >-
  Electronics stack reference (microcontroller firmware on ESP32/Arduino-
  class boards built with PlatformIO, sensors, actuators, wiring and power)
  for the milestone-loop workflow. NOT an invocable skill — the generic
  workflow skills read this document via a relative path when the
  project's CLAUDE.md lists `electronics` in its `Stack:` line. Each
  section below maps to one workflow skill.
disable-model-invocation: true
---

# Electronics stack reference

Stack-specific rules for embedded projects, consumed by the generic
workflow skills. Each section is applied by the skill it is named after,
at the point its preflight says to read this document. Rules here have the
same force as the invoking skill's own rules.

**Also load `physical-build`** (`../physical-build/SKILL.md`, or by name)
and apply its sections the same way. It holds the design/build milestone
kinds, hazards, measured dimensions, the BOM and the as-built record.

## plan-milestones

- **Hardware questions.** Ask, and record in CLAUDE.md: the boards (exact
  model and revision — two revisions of one board can differ in pins and
  USB), how each is powered (mains, battery, solar; the budget), where it
  lives (indoor, outdoor, greenhouse humidity → enclosure rating), how
  nodes talk (wired, Wi-Fi, LoRa…), and what each output drives.
- **Toolchain.** Default: PlatformIO. Record the exact `pio` command in
  CLAUDE.md — it is often not on PATH (e.g.
  `~/.platformio/penv/bin/pio`). One env per firmware/board pair.
- **Safe state per output (mandatory).** For every actuator (relay, pump,
  heater, motor, valve) record what it does on boot, reset, firmware hang
  and power loss, and which of those is safe. Pick normally-open or
  normally-closed contacts on purpose, so loss of the controller leaves the
  safe state. This feeds `physical-build`'s failsafe-first ordering.
- **First milestone** (`Kind: design`, the board on its `Parts:` line).
  A probe firmware on the real board: it reports what
  is actually wired (pins, buses, sensor IDs, supply voltage) over serial,
  plus a measured current draw for the power budget. Pin assumptions are
  trusted only after the probe confirms them.
- **Code layout.** Record in CLAUDE.md: one header is the single source of
  truth for pins and board differences; logic that needs no hardware
  (protocols, control, parsing, calibration math) lives in a library free
  of the framework so native host tests can cover it; one `src/<firmware>/`
  per firmware.
- **Mains voltage.** Any milestone that wires mains says in its Notes that
  the wiring is done or checked by a qualified electrician, and its
  Hazards section says so again.

## next-milestone / bootstrap

- **Toolchain-alive check (mandatory before firmware work).** Run the
  recorded `pio --version`. If it fails, stop and tell the user to install
  PlatformIO Core (or fix the recorded path).
- **Board check (only when this milestone flashes or reads a board).**
  List connected devices (`pio device list`). If the board isn't there,
  ask the user to plug it in. Building and host tests never need it.

## next-milestone / quality gates

- **Build every env** the milestone touches, zero warnings added; run the
  native host tests (`pio test -e native` or the project's command).
- **Pins and board facts only in the pin header.** Never a pin number in
  firmware code.
- **Safe outputs in code.** Outputs are set to their safe state first
  thing in `setup()` (before any slow init), a hardware watchdog is on in
  every firmware that drives an actuator, and a lost sensor or link moves
  outputs to the safe state rather than holding the last command.
- **No blocking control loop.** No long `delay()` in a loop that also
  watches sensors or safety inputs; use timers/state machines.
- **Verify, don't trust, a sensor.** A new sensor reading is checked
  against a reference measurement (a thermometer, a multimeter, a known
  weight) before any logic depends on it; the calibration and its source
  go in the code next to the constant.
- **Secrets** (Wi-Fi passwords, keys, tokens) stay out of the repository:
  an ignored header or env file, with a committed example.
- **Flashing a known board.** Flash only when the target is unambiguous:
  one board connected, or the port resolved from the chip's MAC/serial
  number. USB port names shuffle when boards are replugged.

## next-milestone / agent-executed testing

Tier-1 steps the agent drives itself:

- Build all touched envs; run the native host tests.
- With the board connected: flash it, open the serial monitor, read the
  boot log and the probe/status lines, and drive anything the firmware
  accepts over serial.
- Cross-check readings that two sources can give (two boards hearing each
  other, a sensor against the value the user reads off a reference).
- Prerequisites to ask the user for, if missing: the board plugged in and
  powered; for radio tests, every node it talks to.

Left to the user (tier 2): physical stimuli (heat, water, movement),
wiring, measurements with their instruments, field range.

## next-milestone / testing doc

- **Wiring:** for any milestone that adds or changes connections, a
  connection table (from | to | wire/signal | note) or a diagram image.
- **Power-loss step:** for any milestone that adds an actuator, one tier-2
  step that cuts the controller's power (and one that resets it) and
  checks the output lands in its recorded safe state.

## find-parallel

- **Hotspots:** the pin header, `platformio.ini`, the shared protocol or
  logic library.

## next-group

- **Board access.** Members build and run host tests in their worktrees;
  nobody flashes a board there. Flashing and on-board tests run at the
  integration check, in the main tree, one member after another.

## close-milestone

- **Build check (before committing).** Every env in `platformio.ini`
  still builds — a shared-header change can break a firmware this
  milestone never opened.
- **Secrets.** No credentials in the diff; if one slipped in, remove it
  and tell the user to rotate it.
