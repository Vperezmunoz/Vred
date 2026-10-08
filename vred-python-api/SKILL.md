---
name: vred-python-api
description: Look up the Autodesk VRED Python API offline — services, classes, method signatures, enum values and shipped example scripts. Use whenever writing, reading, debugging or reviewing VRED Python (vrNodeService, vrMaterialService, vrdNode, vrdMaterial, vrScenegraphService, vrFileIO, vrImmersiveInteractionService, VRED terminal scripts, script plugins) instead of guessing signatures or fetching Autodesk help pages.
---

# VRED Python API lookup

**Index version: VRED 2027.1 (`VREDPro-19.1`).** For another release use the matching branch of the repo.

The full VRED API reference (8779 members, 690 classes, 152 example scripts) is indexed
in `data/`. **Query it with `vredapi.py`; never read the files in `data/` directly** — a
single class page is thousands of tokens, a query is tens.

Run from this skill's directory (use `py`, not `python`):

```
py vredapi.py find <regex> [--api v1|v2] [--kind method|data] [-n 40]
py vredapi.py show <Owner.member>       # signature, every param, return, notes
py vredapi.py class <Owner> [regex]     # one-line summary of every member
py vredapi.py classes [regex] [--kind service|class|enum|module]
py vredapi.py enum <EnumName>           # values + meaning; short name is fine
py vredapi.py examples [regex]          # 152 shipped scripts (web ones include HTML/JS)
py vredapi.py example <name>            # print one
py vredapi.py grep <regex>              # search inside the example scripts
py vredapi.py doc <page>                # v2-overview, scenegraphs, webinterface,
                                        # CommandLineParameters, EnvironmentVariables_VRED
py vredapi.py meta                      # which VRED build the index came from
```

Typical flow: `find` to locate the call, `show` to get its exact parameters, `grep` to see
it used in real code. Answer from these results, not from memory — VRED renames methods
between releases and the index is the installed build's own documentation.

## Which service does what

`vrNodeService` find/clone/traverse nodes · `vrScenegraphService` scene tree, selection,
grouping · `vrMaterialService` create/find/apply materials, material graph ·
`vrGeometryService` create and edit geometry · `vrCameraService` cameras, viewpoints ·
`vrLightService` lights, light profiles · `vrRenderSettingsService` raytracing, AA,
render passes · `vrFileIOService` load/save/import/export · `vrSceneplateService`
overlays, HUD, frontplates · `vrWebEngineService` HTML/video on textures ·
`vrImageService` render images, screenshots · `vrBakeService` lightmap/texture baking ·
`vrUVService` UV layout, unwrap · `vrDecoreService` remove hidden geometry ·
`vrVariantService` variant sets · `vrConstraintService` aim/position constraints ·
`vrAnnotationService` annotations · `vrMetadataService` metadata sets and tags ·
`vrQueryService` scene queries/statistics · `vrObjectService` object ids and types ·
`vrMathService` transform maths · `vrGUIService` menus, docking, VRED windows ·
`vrDeviceService` input devices · `vrHMDService`, `vrImmersiveInteractionService`,
`vrImmersiveUiService` VR · `vrPhysicsService` collisions, rigid bodies ·
`vrClusterService`, `vrClusterManagerService` render cluster · `vrSessionService`
collaboration · `vrLiveReferenceService`, `vrReferenceService` references ·
`vrAssetsService` asset manager · `vrGPUService` GPU info · `vrLogService`,
`vrProgressService`, `vrMessageService`, `vrUndoService` housekeeping.

Full list: `py vredapi.py classes --kind service`.

## API v1 vs v2 — get this right

- **v2** (`vr*Service` + `vrd*` object classes) is the current API. Prefer it always.
- **v1** is the legacy flat module API (`vrFileIO.load()`, `findNode()`, `setTransparency()`).
  Still works and still appears everywhere in old customer scripts, so read it — but do not
  write new code against it. Index rows for v1 are tagged `[v1]`.
- Many v1 functions are exposed as bare globals in VRED's terminal; v2 services are injected
  as bare names too, so `import` is optional inside VRED but harmless.
- **Inside a script plugin the rule is stricter: v2 services are injected as bare names,
  v1 modules are not.** `vrOSGWidget`, `vrController` and the other legacy modules need a
  real `import vrOSGWidget`; without it every call raises `NameError`, which a defensive
  `try/except` will happily convert into a plausible-looking zero. See the
  `vred-script-plugin` skill.
- `vrd*` classes are handles to scene objects. Test with `isValid()`; a stale handle after a
  scene reload silently does nothing.
- Enum values live on `*Types` classes, e.g. `vrMaterialTypes.MaterialType.Phong`,
  `vrRenderTypes.…`. Use `enum` to get the exact spelling — these are the most common source
  of `AttributeError` in VRED scripts.
- Overloads share one name: `find` may show several `findNodes(...)` rows. Match parameter
  count and types to the one you want; VRED resolves by arity and type.
- **When a docstring says "see examples/snippets/X", go read it.**
  `vrRenderSettings.setRaytracingMode` points at `snippets_setRenderer`, and that snippet
  holds the only written-down mapping of renderer names to the two-call
  `getRaytracingEnabled()` + `getRasterizationMode()`/`getRaytracingMode()` combination.
  `py vredapi.py examples <regex>` first — the indexed name carries a `snippets_` prefix,
  so `example setRenderer` fails while `example snippets_setRenderer` works.
- **Signals are indexed like methods, and `find` misses them.** A guess such as
  `find "[Vv]iewpoint.*activ"` returns nothing while
  `vrVariantService.variantSetExecuted(variantSetNode)` sits in the index the whole time.
  Before concluding "no signal exists, poll instead", run `class <Service>` and read the
  tail of the listing, where the signals are grouped.
- **Inherited members are listed on the class that defines them**, not on the subclass.
  `vrdNode` shows `[inherits vrdSceneObject]`, so `vrdNode.isValid()` is real but only turns
  up under `class vrdSceneObject`. If a member seems missing, walk up the inheritance line
  or search unanchored: `find "\.isValid"`.

`references/starters.md` holds a page of verified boilerplate (find nodes, apply a material,
load a file) for when the task is routine.

## Related

- Building an actual VRED **script plugin** (panel under the Scripts menu, PySide6 UI,
  install layout, Web Engine gotchas): use the `vred-script-plugin` skill. This skill is
  the API reference; that one is the hard-won behaviour that the docs get wrong.

## Rebuilding for a newer VRED

The index is generated from `<VRED install>\doc\_sources` plus the built example HTML:

```
py build_index.py                       # newest VREDPro install found
py build_index.py "C:\Program Files\Autodesk\VREDPro-2027\doc\_sources"
```

`py vredapi.py meta` reports the build the current index was made from. Regenerate after
installing a new VRED so signatures match what the user is actually running.

**Internal version vs marketing year.** Installs are named `VREDPro-19.1` while the product
is sold as VRED 2027.1 (`VREDPro-19.0` = 2027, `18.2` = 2026.2). An index reporting `19.1`
*is* the 2027.1 documentation — don't warn that it might be stale, and don't go looking for
a `VREDPro-2027` folder.
