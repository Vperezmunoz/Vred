---
name: vred-perf-comparison
description: Build a one-pager HTML/PDF comparing two VRED FPS perf-test logs (e.g. regular rendering vs. static foveation, or any two capture sessions on the same rig). Use when given two or more `*_perftest_fps_log_*.txt` files and asked to compare, chart, or report on FPS across matched scenarios.
---

# VRED perf-test log comparison

## Log format

Tab-separated `Automotive_*_perftest_fps_log_*.txt` files from a VRED Vulkan/OpenXR
benchmark run. `#`-prefixed header lines give VRED build, OS, CPU, RAM, GPU(s),
OpenGL/driver, raytracing support, and OpenXR runtime. One file can contain **multiple
session blocks** (`# Session started ...`) on different days or VRED builds — read the
whole file and split by session before assuming which rows belong together.

Data columns: `Timestamp, Context, Engine, DLSS, RT Reflections, Env Shadows, Avg FPS,
Min, Max, Duration(s), Samples`.

## Matching scenarios across logs

1. A scenario is comparable only if the exact tuple (Context, DLSS, RT Reflections, Env
   Shadows) exists in **both** logs. Drop anything that only appears on one side (e.g. a
   DLSS mode, or a Context label, unique to one log) — say explicitly what got dropped
   and why.
2. If a log has multiple sessions on different VRED builds/dates, prefer the pair of
   sessions that share the same VRED build and are closest in time, and say which
   session(s) got excluded and why.
3. **Never silently relabel a Context.** If the user asks to treat one label as another
   (e.g. "treat VSet as Interior") on log A, apply it only to log A — don't assume the
   same relabel applies to log B's own use of that Context name, unless told to.
4. Collapse repeat runs of the same tuple within one session into a single
   sample-weighted mean: `avg = Σ(avg_i · n_i) / Σ(n_i)`, `min = min(min_i)`,
   `max = max(max_i)`. Report the merged sample count too.
5. State plainly whether the two logs are separate capture sessions (not a true in-run
   A/B) — that's a real caveat on how much of the FPS delta to attribute to the setting
   under test vs. session variance (thermal state, background load, view state).

## Report layout for a one-pager

- Follow the `dataviz` skill for the chart itself (categorical palette, mark specs,
  hover tooltips, legend, accessibility pass) even though this is a static report, not
  a live dashboard.
- Merge system-info into one block when both logs came from the same physical machine —
  don't duplicate identical CPU/GPU/OS/driver rows per log; only show what actually
  differs (session timestamp, the setting under test) per side.
- Group scenarios into columns by a natural dimension (e.g. Exterior vs. Interior)
  instead of one long vertical list — keeps bar lengths meaningful at a glance and the
  page shorter.
- Put the full numeric backing table behind a collapsed `<details>` (hidden from print
  via `@media print { details.data-toggle { display: none } }`) rather than always
  showing it — the chart + a short caveat paragraph is normally enough.
- For a single printable page: set `@page { size: A4 portrait; margin: 8mm; }` and add a
  **separate** `@media print` block that independently shrinks every font-size, padding
  and margin used on screen. Screen-friendly sizing does not fit one printed page by
  itself — budget roughly (masthead + system-info + chart + notes) against ~281mm of
  usable A4-portrait height at 8mm margins, and iterate the print font sizes down if it
  still overflows.
- Keep "Notes & caveats" to 2–3 dense sentences covering: matching rule, any relabeling
  applied, and the session-variance caveat — this section overflows a one-pager fastest.
- Masthead: product logo + title + attribution line (e.g. "Created by <name>"),
  referenced via a `file:///` URI with spaces percent-encoded if the image is local.
