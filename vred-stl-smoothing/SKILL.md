---
name: vred-stl-smoothing
description: Make STL meshes render smooth in Autodesk VRED instead of faceted (weld vertices, repair triangle orientation, smooth normals with a crease angle), plus an "orientative" defect colour map for stamping surfaces. Use when a task mentions STL in VRED, faceted/triangulated mesh, no normals, stamping or CAE mesh export, a displacement-texture workaround for deformation, or the STLSmooth plugin - it holds the finished plugin source, the algorithm, what was verified in VRED and what was not.
---

# STL smoothing in VRED (STLSmooth)

## The problem and the answer

An STL stores every triangle on its own: 3 loose corners and one flat normal per face, no
shared vertices. VRED has nothing to average, so it shades each triangle flat. **The mesh is
fine; only connectivity is missing.** Fix = weld coincident vertices, make winding
consistent, compute smooth vertex normals with a crease angle. Do **not** go down the
"displacement texture to fake the deformation" route: it needs textures, alignment and
height calibration, and is only an approximation of the real simulation geometry.
(That route was tried first: a 4096x4096 16-bit grayscale PNG, mid-grey 0.5 = zero
displacement, edges faded to exactly 0.5. It worked as a texture but was the wrong tool.)

Typical case: a stamping simulation (CAE tool) exports STL, ~2.5 mm shell elements, open
sheet, ~8k triangles for a small part. A sample part welded cleanly: 24,930 soup vertices ->
4,283, 254 boundary edges (open sheet outline, normal), 0 non-manifold.

## What is in this skill

- `plugin/STLSmooth/` - `vrSTLSmooth.py`, `DISCLAIMER.txt`, `STLSmooth_ramp.png`. This is the
  finished plugin. `plugin/README.md` is the end-user README (install, use, settings,
  troubleshooting, "why it differs from your CAE tool").
- `stl_smooth_numpy.py` - standalone numpy STL -> smoothed OBJ converter (needs numpy; VRED's
  own Python has no numpy, which is why the plugin is pure Python).
- `tests/` - offline tests with a PySide6/VRED stub (see "Testing").
- Install = copy the three plugin files into
  `Documents\Autodesk\VRED-<version>\ScriptPlugins\STLSmooth\` (keep the PNG next to the .py;
  `Documents` may be OneDrive-redirected on managed machines).
- To hand it out: build a `<Tool>-Share` folder with the zip + README, then extract the zip to a
  temp dir, grep it for personal strings (user name, home paths, customer names), compare the
  extracted .py with the source, and rerun the tests against the extracted copy.

## Plugin features (final state)

Smooth (import STL / folder / selected), orientation repair, progress bar + Cancel
(chunked generators), keep original (smooth a copy) with all versions in a switch node
`<part>_versions`, optional Phong subdivision, defect colour map (local deviation in mm,
secondary mode curvature) with an **orientative** label. A zebra feature was built and
**removed** (see below).

## Algorithm notes

- Weld: quantise positions with tolerance (default 1e-4 of largest dimension) into a dict.
- Orientation: edge->faces map, flood fill per connected patch across manifold edges; a face
  is flipped when it uses an edge in the same direction as its neighbour; if more than half
  a patch was flipped, flip the whole patch back (keep majority winding). Reports flipped /
  patches / conflicts. Tested: 30% flipped faces repaired exactly; 70% flipped -> consistent
  but facing down (design: majority wins; an inside-out export stays inside-out).
- Normals: angle-weighted, a corner only averages faces within the crease angle (default
  40 deg); vertices on creases are duplicated, one per normal. Output goes to
  `vrdGeometryNode.setPositions/setIndices/setNormals` (flat float lists; indices refer to
  positions; normal buffer same size as positions).
- Defect "local deviation": signed distance of each vertex from a biweight-weighted local
  average (bins of radius/4, cells of radius), along the area-weighted vertex normal.
  Design shape larger than the radius cancels; dents/buckles up to ~radius show. A dent reads
  shallower than true depth (reference partly follows it; test: 0.3 mm dent -> -0.20 mm) with a faint
  opposite ring. Auto colour range = 99.9th percentile of |value| (deviation) / 98th (curvature).
  Curvature = |dn . dp| / |dp|^2 averaged over edges.
- Speed (pure Python): 180k triangles smooth 2.3 s, deviation 3.9 s, curvature 2.6 s;
  1M triangles smooth ~15 s. Deviation cost does not depend on the radius.
- Colour map display: U coordinate (V = 0.5) written to texture slot 0 with `setTexCoords`,
  material with a 256x4 colour-ramp PNG, clamp repeat, UV mapping, incandescence 0.5 so colours
  read on unlit sides.

## What does NOT work / hard-won VRED facts

- **A texture image built in memory is not accepted**: `vrImageService.loadImage(QImage, "name.png")`
  + `tex.setImage(img)` left the diffuse slot of the material EMPTY (grey surface, no error).
  Fix that worked: ship the PNG next to the plugin and `vrImageService.loadImage(path)`;
  write the file from code only as a fallback if it is missing. Re-apply the textures every
  time the material is reused so a material broken by an old version gets repaired.
- **VRED surface analysis ("zebra") is OpenGL-only** (`vrSurfaceAnalysis.enableSurfaceAnalysis`
  etc., v1 module, undocumented int values for mode/line type). Did not work in Vulkan. A
  baked isophote copy (U = angle(normal, axis) * stripes/180 + 0.25 on a repeating black/white
  texture) is renderer-independent but shared the empty-texture bug above; zebra was dropped
  for simplicity. Rebuild only if asked.
- Selecting `_smooth_` copies as sources: the defect map first ignored them as "earlier results"
  and did nothing visible (short log line only). Analysis runs must accept smoothed copies and
  skip only earlier analysis copies; one result per part when original + copy are both selected.
- Name collisions: matching copies by `startswith(base)` also hit `PartA2` when handling `PartA`.
  Match `name == base` or `startswith(base + tag)`.
- Switch node: `vrScenegraphService.createNode(vrScenegraphTypes.NodeType.SwitchNode, parent, name)`,
  `switch.children.append(node)` moves a node in, `vrdSwitchNode(...).setChoice(index)` shows it.
  VRED may rename for uniqueness (`_versions1`) -> match with `startswith`. Switch node has no
  transform, so parts do not move. Not yet confirmed in VRED at time of writing: that
  the switch shows the newest version and that the annotation follows switch visibility
  (`vrAnnotationService.createAnnotation`, `setSceneNode(geo)`, `setUseSceneNodeVisibility(True)`).
- `vrdGeometryNode(node)` cast is needed after `node.isType(vrdGeometryNode)`.
- Duplicating a geometry: `vrScenegraphService.duplicateNodes([n], vrScenegraphTypes.DuplicateOption.DuplicateAll)`.

## The defect map is ORIENTATIVE - say so everywhere

Users may compare the map with their CAE tool and distrust VRED if numbers differ. The map is
a geometric estimate from the exported mesh (compared to a smoothed version of itself), not
the solver's criteria (nominal die surface, thinning, strain, stoning, curvature defects).
Keep the caveat in: panel note, log line, in-scene annotation, legend wording ("approx."),
README section *Why it differs from your CAE tool*, and DISCLAIMER. Honest scope: works well
on large gently curved outer panels; on a small deep cup (the sample part) it mostly shows
the part's own walls and radii. Best long-term: ask whether the CAE tool can export its own
per-vertex results (thinning, defect criterion) and show those via the same U-coordinate
colour-ramp mechanism.

## Testing offline (do this before every VRED round trip)

Stub PySide6 (QtCore/QtGui/QtWidgets) and the VRED names, import the plugin, and drive the
generators directly. `tests/test_robust.py` (flipped-face repair, 180k/1M synthetic timing),
`test_defect.py` (known dent on a curved panel), `test_ui.py` (mock panel run, progress,
cancel, defect copies), `test_tex.py` (material repair), `test_switch.py` (switch/annotation).
Pass an STL path and the plugin file as arguments; also run them against the **extracted
zip**, not just the source. A mock run caught real bugs (progress loop with `frac` unbound
on a slow tick; a similarly named part being hidden; duplicate defect copies). Before the
first in-VRED test, say what is unverified.

## Tooling lessons from this build

- Large Python patches through a bash heredoc broke repeatedly (nested quotes, `\n` in
  strings turning into real newlines). Write the patch script to a file and run it with
  `py -I script.py args`; make each replacement `assert count == 1`.
- Use `py -I` for every script that reads untrusted STL/zip data.
- Every VRED call that can fail should log once (`_call(label, fn, *args)` pattern) instead
  of raising or silently passing; then a pasted panel log shows the cause.
- VRED internal versions: 19.0 = 2027, 19.1 = 2027.1, 19.2 = 2027.2.
