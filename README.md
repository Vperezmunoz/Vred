# VRED Claude Skills

> **This branch targets VRED 2027.1 (internal build `VREDPro-19.1`).**
> The `vred-python-api` index matches that release. Using VRED 2027.2? Switch to the `vred-2027.2` branch. Not sure which you have? Your install folder is named `VREDPro-19.1` for 2027.1 or `VREDPro-19.2` for 2027.2.

| Your VRED | Clone branch |
| --- | --- |
| 2027.1 (`VREDPro-19.1`) | `vred-2027.1` |
| 2027.2 (`VREDPro-19.2`) | `vred-2027.2` |

Claude Code / Claude Agent "skills" for working with Autodesk VRED — Python API lookups, script plugin development, and packaging tools for customers.

A skill is a folder with a `SKILL.md` that Claude Code loads on demand when its description matches the task at hand. See [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) for how they work.

## Skills in this repo

### [vred-python-api](vred-python-api/)
Offline lookup for the full VRED Python API (690 classes, 8779 members, 152 shipped example scripts). Query it with `vredapi.py` instead of guessing method signatures or fetching Autodesk help pages — covers services, classes, enums, and both the v1 and v2 API surfaces.

### [vred-script-plugin](vred-script-plugin/)
Practical guide to building, installing, and debugging VRED Python script plugins — Scripts-menu panels, PySide6 UI, materials, and Web Engine video/HTML textures. Documents behavior that Autodesk's own docs get wrong, established by testing against a real VRED build.

### [vred-vlm-review](vred-vlm-review/)
How to build an AI design-review copilot on VRED: an in-VRED capture trigger (camera settle or variant set) plus an external Python worker that sends the on-screen render to a vision-language model and returns a critique as a carousel card and an in-scene frontplate HUD. Covers the sceneplate API, capturing without re-rendering, swapping between cloud and local VLM backends, and stopping the model from repeating itself.


### [vred-perf-comparison](vred-perf-comparison/)
Build a one-pager HTML/PDF comparing two VRED FPS perf-test logs (e.g. regular rendering vs. static foveation) — matching scenarios across logs, collapsing repeat runs into weighted means, and laying out a print-ready single-page report.

## Using these skills

Clone this repo (or a subset of it) into your Claude Code skills directory, e.g.:

```
git clone --branch vred-2027.1 https://github.com/Vperezmunoz/Vred.git skills
```

Claude Code picks up any `SKILL.md` it finds under the configured skills path and loads a skill automatically when the task matches its description, or on explicit request (e.g. `/vred-python-api`).

## Branch note

This is the `vred-2027.1` branch. `main` in this repository is an unrelated project (WASD navigation / SoundEmitter) — don't merge the two.
