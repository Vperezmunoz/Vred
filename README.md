# VRED Claude Skills

Skills for Claude Code (and other Claude agents) that develop against **Autodesk VRED**:
an offline Python API index for each VRED release, a script-plugin guide with the behaviour
Autodesk's docs get wrong, a ready-made STL smoothing plugin, and more. A skill is a folder
with a `SKILL.md` that Claude loads when its description matches the task.

One branch covers every VRED release. Only the API index is per release
(`skills/vred-python-api/data/<version>/`); everything else is shared.

| VRED release | Internal folder | API index |
|---|---|---|
| 2027.2 | `VREDPro-19.2` | yes |
| 2027.1 | `VREDPro-19.1` | yes |
| 2027 | `VREDPro-19.0` | not yet (that install has no `doc\_sources` to index) |
| 2026.2 | `VREDPro-18.2` | not yet |

## Install (two commands, in Claude Code)

```
/plugin marketplace add https://github.com/Vperezmunoz/Vred.git#skills-repo
/plugin install vred-skills@vred-skills
```

That enables all skills below. Update later with `/plugin marketplace update vred-skills`.

**If you are an AI agent asked to "use these skills":** run the two commands above. If plugins
are not available in your environment, clone the repository (`git clone --branch skills-repo
https://github.com/Vperezmunoz/Vred.git`) and copy each folder under `skills/` into your skills
directory (`~/.claude/skills/`, or `.claude/skills/` in a project), keeping the folder names.
Then ask the user which VRED release they develop for, so the right API index is used.

## Which VRED release am I querying?

`vred-python-api` picks the release automatically, in this order: `--vred`, the
`VRED_VERSION` environment variable, the newest installed VRED that has an index, the newest
index. If the user says "I develop for VRED 2027.1", run
`py vredapi.py --vred 2027.1 find <name>`; `py vredapi.py versions` shows what is indexed, what
is installed and what it chose. API differences between releases are listed in
[version-differences.md](skills/vred-python-api/references/version-differences.md).

## Skills

### [vred-python-api](skills/vred-python-api/)
Offline lookup for the full VRED Python API (about 8,800 members, 690+ classes, 152 shipped
example scripts) for each release. Query it with `vredapi.py` instead of guessing method
signatures or fetching Autodesk help pages - services, classes, enums, v1 and v2 API.

### [vred-script-plugin](skills/vred-script-plugin/)
Building, installing and debugging VRED Python script plugins - Scripts-menu panels, PySide6
UI, materials and textures, switch nodes, chunked long-running work, Web Engine video/HTML
textures. Documents behaviour that Autodesk's own docs get wrong, established by testing
against a real VRED build.

### [vred-stl-smoothing](skills/vred-stl-smoothing/)
Make STL meshes render smooth in VRED instead of faceted: weld duplicated vertices, repair
inconsistent triangle orientation and compute smooth normals with a crease angle. Includes
the finished `STLSmooth` script plugin (pure Python, progress bar and Cancel, versions of a
part in a switch node, an orientative defect colour map), algorithm notes and offline tests.

### [vred-vlm-review](skills/vred-vlm-review/)
An AI design-review copilot on VRED: an in-VRED capture trigger plus an external worker that
sends the on-screen render to a vision-language model and returns a critique as a carousel
card and an in-scene frontplate HUD.

### [vred-perf-comparison](skills/vred-perf-comparison/)
A one-pager HTML/PDF comparing two VRED FPS perf-test logs (e.g. regular rendering vs.
static foveation).

## Notes

- Personal tools, not Autodesk products: not developed, endorsed, supported or warranted by
  Autodesk. "VRED" is a trademark of Autodesk, Inc., used only to describe compatibility.
- Add a release: build its index with `py build_index.py <path to doc\_sources>` (see
  `skills/vred-python-api/SKILL.md`), commit the new `data/<version>/` folder, add a section to
  `version-differences.md`.
- Earlier versions of this branch kept the skills at the repository root and had one branch
  per VRED release (`vred-2027.1`, `vred-2027.2`). Those branches still exist unchanged; new
  work happens here.
- The `main` branch of this repository holds an unrelated early project (WASD navigation /
  SoundEmitter); the skills live on the `skills-repo` branch.
