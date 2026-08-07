# WASD Navigation

Game-style **WASD flythrough navigation** for the VRED viewport, with an on-screen status
plate showing the current state and speed.

*Community script. Not an Autodesk product — not developed, endorsed or supported by
Autodesk.*

## What's in this folder

| File | Purpose |
| --- | --- |
| `WASDNavigation.py` | The script. Run it from VRED's Script Editor. |
| `README.md` | This document. |

## Requirements

VRED with either PySide6 or PySide2 — the script detects which is available and adapts, so
it works across older and newer VRED releases.

## Install

This is a **Script Editor script**, not a script plugin — there is nothing to install into
`ScriptPlugins`.

1. Open `Scripts > Script Editor` in VRED.
2. Paste in the contents of `WASDNavigation.py`.
3. Run it.

The script cleans up any previous instance of itself on the way in, so you can re-run it
after editing without restarting VRED or ending up with duplicate status plates.

To start with a different movement speed, change the last line:

```python
wasd_nav = WASDNavigation(speed=2000.0)
```

## Controls

| Key | Action |
| --- | --- |
| `X` | Toggle WASD navigation on / off |
| `W` / `S` | Move forward / backward |
| `A` / `D` | Strafe left / right |
| `Q` / `E` | Move down / up |
| `LMB` / `RMB` drag | Look around (inside the viewport only) |
| Mouse wheel | Adjust speed in steps of 250 |
| `Shift` | Move 2x faster while held |

## Status plate

A frontplate inside the viewport shows the current state:

- **Active** — current speed, plus a hint for switching back off
- **Inactive** — "Press X to switch to WASD navigation"

## Known issue

While WASD navigation is **active, VRED's UI can't be interacted with** — the script is
holding the keyboard. Press `X` to switch it off before using menus or panels.
