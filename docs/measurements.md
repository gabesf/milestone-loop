# Measurements

Baseline for the 0.8.0 performance changes, measured with
`plugins/milestone-loop/scripts/measure-sessions.py` on two projects that run
the workflow: AI Runner (web, Vite + Three.js) and Transformers Final Battle
(Unity).

## Baseline (before 0.8.0)

| Unit | Date | Implementer active (min) | Implementer calls | Reviewer runs | Capture (min) | Images | Largest context | AskUserQuestion calls |
|---|---|---|---|---|---|---|---|---|
| M-18 (single) | 2026-09-17 | 14 | 79 | 5 | 0 | 0 | 140k | 0 |
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
