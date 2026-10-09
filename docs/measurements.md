# Measurements

Baseline for the 0.8.0 performance changes, measured with
`plugins/milestone-loop/scripts/measure-sessions.py` on two projects that run
the workflow: AI Runner (web, Vite + Three.js) and Transformers Final Battle
(Unity).

## Baseline (before 0.8.0)

| Unit | Date | Implementer active (min) | Implementer calls | Reviewer runs | Capture (min) | Images | Largest context | AskUserQuestion calls |
|---|---|---|---|---|---|---|---|---|
| M-18 (single) | 2026-09-17 | 16 | 87 | 4 | 0 | 0 | 140k | 0 |
| M-31, M-32, M-33 (parallel) | 2026-09-25 | 132 | 464 | 8 | 37 | 112 | 511k | 0 |
| G-04: M-41, M-42, M-43 | 2026-10-01 | 292 | 880 | 13 | 54 | 119 | 627k | 4 |
| M-56 (Unity) | 2026-09-30 | 196 | 500 | 7 | 19 | 18 | 968k | 7 |

What the numbers say:

- **Latency.** A model call takes the same time as before: the median is 6–8 s across models, effort levels and context sizes. Time follows the number of calls, capture time and round trips to the user.
- **Fixed cost per milestone.** A small change pays the full package: process criteria copied into each milestone, docs sync, capture at several screen sizes, a 3-reviewer gate with a second round, and the records.
  - M-32 only removed an on-screen reminder. It took 126 model calls, 74 of its tool calls were captures, and it ended with 10 deviation entries.
  - Changes of the same size made outside the cycle took 2–3 minutes.
- **Decisions in mid-implementation.**
  - G-04: one visual parameter went back to the user 6 times and accounted for 54 % of the critical path.
  - M-56: one decision waited 701 minutes for an answer overnight.
- **Gate.** Time per milestone did not grow (median ~29 min). Doc and comment findings went from 16 % to 36 % of all findings. A second round found behavior bugs only after fixes that changed runtime code.

## Targets for 0.8.0

| Metric | Target |
|---|---|
| A `Size: S` change, from request to hand-over | ≤ 20 min |
| Implementer active time, other milestones | −40 % |
| Capture time per implementer | −50 % |
| AskUserQuestion calls after plan approval | ≤ 1 per milestone |
| Largest context of any agent | < 300k |

## After 0.8.0: the gate and the waits (2026-10-08)

Four units on Subway Surfer (web) and Transformers Final Battle (Unity),
read from the subagent timelines rather than from summed active time: the
3 reviewers run in parallel, so G-13's 91 reviewer-minutes were about 36 on
the clock.

| Unit | Gate on the clock | Bugs lens | Other two lenses | Fixes and round 2 | Your test |
|---|---|---|---|---|---|
| M-57 | 27 min | 20.5 | 6.4 / 8.2 | none | 93 min (spike verdict) |
| G-13 (M-61 path) | 57 min | 16.6 | 6.4 / 9.9 | 11.5 + 9.3 + 0.9, integration 12 | 12 min |
| M-58 | 77 min | 32.7 | 12.2 / 13.0 | 19.9 + 9.1 + 8.8 | 14 min |
| M-63 (`Size: S`) | 12.5 min, alongside tier 1 | 12.5 | — | — | 11 min |

What the numbers say:

- **The gate lasts as long as its slowest lens**, always the bugs lens, 2–3× the other two.
- **Fixes changed runtime code in 3 of 4 full gates**, so a second round ran. Tier 1 ran after the gate, never alongside it.
- **The close asked for the green light twice.** The user had run `/close-milestone` or said "go"; the skill asked again. Cost: 24 min (M-57), 41.5 min (G-13), 932 min overnight (M-63).
- **The metrics overstated waits on the user.** A wait ended by a subagent's report was counted as the user's when an attachment line came first, and the user's messages while implementers ran counted as waits: 100 of M-58's 114 user minutes. M-63's line also repeated G-13's numbers, because both ran in one session.

## Targets for the next release

| Metric | Target |
|---|---|
| Gate plus tier 1 on the clock, full gate | −25 % (lenses rebalanced, bugs lens split for multi-implementer diffs, tier 1 alongside) |
| Waits on the user at close | one step: running `/close-milestone` |
| Decisions holding a session overnight | none with a recommended option and a local effect |
