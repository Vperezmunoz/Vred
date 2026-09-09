# VRED Claude Skills

Claude Code / Claude Agent "skills" for working with Autodesk VRED — Python API lookups, script plugin development, and packaging tools for customers.

A skill is a folder with a `SKILL.md` that Claude Code loads on demand when its description matches the task at hand. See [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) for how they work.

## Skills in this repo

### [vred-python-api](vred-python-api/)
Offline lookup for the full VRED Python API (690 classes, 8779 members, 152 shipped example scripts). Query it with `vredapi.py` instead of guessing method signatures or fetching Autodesk help pages — covers services, classes, enums, and both the v1 and v2 API surfaces.

### [vred-script-plugin](vred-script-plugin/)
Practical guide to building, installing, and debugging VRED Python script plugins — Scripts-menu panels, PySide6 UI, materials, and Web Engine video/HTML textures. Documents behavior that Autodesk's own docs get wrong, established by testing against a real VRED build.

### [vred-vlm-review](vred-vlm-review/)
How to build an AI design-review copilot on VRED: an in-VRED capture trigger (camera settle or variant set) plus an external Python worker that sends the on-screen render to a vision-language model and returns a critique as a carousel card and an in-scene frontplate HUD. Covers the sceneplate API, capturing without re-rendering, swapping between cloud and local VLM backends, and stopping the model from repeating itself.

### [customer-shareable-package](customer-shareable-package/)
Checklist and conventions for turning a working local tool into something you can hand to a customer, partner, or colleague — scrubbing personal paths, bundling dependencies with their licenses, README structure, and verifying the shipped artifact instead of the source.

### [vred-perf-comparison](vred-perf-comparison/)
Build a one-pager HTML/PDF comparing two VRED FPS perf-test logs (e.g. regular rendering vs. static foveation) — matching scenarios across logs, collapsing repeat runs into weighted means, and laying out a print-ready single-page report.

## Using these skills

Clone this repo (or a subset of it) into your Claude Code skills directory, e.g.:

```
git clone --branch skills-repo https://github.com/Vperezmunoz/Vred.git skills
```

Claude Code picks up any `SKILL.md` it finds under the configured skills path and loads a skill automatically when the task matches its description, or on explicit request (e.g. `/vred-python-api`).

## Private skills

Two further skills are cloned into this same folder from separate **private** repositories and
are gitignored here. They hold internal and personal information and must never be committed to
this repository, which is public.

## Branch note

This content lives on the `skills-repo` branch. `main` in this repository is an unrelated project (WASD navigation / SoundEmitter) — don't merge the two.
