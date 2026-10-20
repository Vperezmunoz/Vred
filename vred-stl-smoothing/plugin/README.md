# STLSmooth

A VRED script plugin that makes STL meshes render smooth instead of faceted. STL files store
every triangle separately, with no shared vertices and one flat normal per face, so VRED
shows the triangles. STLSmooth welds the coincident vertices back together, repairs
triangles whose orientation is flipped, and computes smooth vertex normals, keeping real
sharp edges sharp with a crease angle. It can also colour a copy of the part by local
deviation or curvature to make stamping defects visible.

Not a product of Autodesk. Not developed, endorsed, supported or warranted by Autodesk.
See `DISCLAIMER.txt` for the full text.

## What's in this folder

| Item | What it is |
|---|---|
| `STLSmooth.zip` | The plugin, ready to unzip into VRED's ScriptPlugins folder |
| `STLSmooth/` | The same contents, unzipped, for browsing before installing |
| `STLSmooth/vrSTLSmooth.py` | The plugin itself (no dependencies) |
| `STLSmooth/DISCLAIMER.txt` | Full disclaimer / no-warranty text |
| `STLSmooth/STLSmooth_ramp.png` | Colour-ramp texture for the defect map - keep it next to the plugin |

## Requirements

- Autodesk VRED 2027 (VREDPro-19.0), 2027.1 (19.1) or 2027.2 (19.2). The mesh processing
  was tested outside VRED; the plugin has not yet been verified inside every version.
- No third-party Python packages (no numpy needed). Nothing to install or download
  beyond this zip.

## Install

1. Locate your VRED `ScriptPlugins` folder:
   `Documents\Autodesk\VRED-<version>\ScriptPlugins\`
   (on machines where `Documents` is redirected to OneDrive, that's
   `OneDrive - <Company>\Documents\Autodesk\VRED-<version>\ScriptPlugins\`).
   `<version>` is the internal number: `19.0` for 2027, `19.1` for 2027.1, `19.2` for 2027.2.
2. Unzip `STLSmooth.zip` directly into that folder. Result should look like:
   ```
   ScriptPlugins\
       STLSmooth\
           vrSTLSmooth.py
           DISCLAIMER.txt
           STLSmooth_ramp.png
   ```
   Not `ScriptPlugins\STLSmooth\STLSmooth\...` - if your unzip tool created that extra
   nested folder, move the inner one up a level.
3. In VRED, go to **Edit > Preferences** and make sure the Python sandbox is disabled.
   This is required for any script plugin to load, not just this one, and it affects every
   script VRED runs afterwards.
4. Restart VRED. The plugin appears under **Scripts > STLSmooth**.

## Use

**Save your scene first - smoothing is not undoable.**

By default the original STL is kept, and every version of a part lives in one switch node
next to where the original was:

```
Sheet_versions            <- switch node: shows one version at a time
    Sheet                 <- the original STL, untouched
    Sheet_smooth_c40_s0   <- smoothed, crease 40 deg, no subdivision
    Sheet_smooth_c25_s1   <- smoothed with other settings
    Sheet_defect_dev20    <- defect map, defect size 20 mm
```

Each run adds one version and makes it the one shown. To compare, pick another child of
the switch in the Scenegraph, or use the switch in a variant set. A switch has no transform
of its own, so nothing moves. Copies already made are skipped as sources, so selecting a
whole group won't copy a copy. Copies made by an older STLSmooth version that sit next to
the original are moved into the switch on the next run. Untick **Compare in a switch node**
to get the older behaviour (copies next to the original, the original hidden).

- **Import STL...** - pick one or more STL files. They are imported into the scene and
  smoothed automatically.
- **Import folder...** - imports and smooths every `.stl` in a folder.
- **Smooth selected** - for STLs already in the scene: select nodes in the Scenegraph
  and click. Every triangle mesh under the selection is processed.

A progress bar shows the part and step being processed; VRED stays usable while it runs,
and **Cancel** stops the run. Nothing is written to the scene until a part is finished, so
cancelling leaves no half-processed part behind (parts finished before the cancel stay).
As a guide, a 1-million-triangle mesh takes about 15-20 s.

The log in the panel reports per part: triangle count, vertices before and after welding,
boundary edges (open sheet outline - normal for a stamping), non-manifold edges (should
be 0; a high count points to a bad export), and how many triangles had their orientation
repaired.

## Orientation repair

Some exports list part of the triangles in the opposite order, so their normals point the
other way; after smoothing these show up as dark patches or hard seams. STLSmooth makes
every triangle agree with its neighbours. Within each connected patch it keeps the
orientation that most of the triangles already had, so a mostly-correct export keeps its
outside side. If a whole part comes out lit from the wrong side, the export itself is
inside-out - flip it with VRED's own normal tools.

## Defect colour map

> **Orientative only.** The defect map is an estimate computed from the mesh geometry in
> VRED. It shows *where* the surface is irregular, not *how much* in a way that matches a
> CAE tool. Its numbers will differ from AutoForm, PAM-STAMP or any other stamping
> simulation - see *Why it differs from your CAE tool* below. Use the CAE results for
> engineering decisions.

Select a part (the original STL or its `_smooth_` copy) and click **Defect map selected**.
It always makes a new copy, `<part>_defect_dev20` or `<part>_defect_curv`, coloured blue -
cyan - green - yellow - red with the shared material `STLSmooth_DefectMap`, added to the
part's switch. The original is never changed. The legend under the button and the log
give the approximate values of the colours, and a label in the scene marks the map as
orientative.

| Mode | What it shows | Colours |
|---|---|---|
| Local deviation (mm) | How far each point sits above or below a smoothed version of the part, measured along the surface normal: dents, low spots, buckles, wrinkles | green = 0, blue = dent (-), red = bump (+) |
| Curvature | How sharply the surface bends (1/mm; 1/value = bending radius) | blue = flat, red = tightest bend |

How to read it:
- **Defect size** sets what counts as a defect: shapes up to about that size show up,
  larger shapes count as the part's design form and stay green. Pick it a bit larger than
  the defects you look for (e.g. 20-50 mm for low spots on an outer panel).
- It works best when the part's own features (radii, steps, beads) are much larger than the
  defect size, as on an outer skin panel. On a small, strongly shaped part, the walls and
  radii themselves show up - that is the method, not a defect.
- A dent reads somewhat shallower than its true depth and has a faint opposite-colour
  ring around it, because the smoothed reference partly follows the dent.
- It is **not** a comparison with the nominal CAD part, and not the stamping solver's own
  results (thinning, strain, surface-defect criteria). Use those for sign-off.
- **Colour range** auto scales to the strongest defects of the part. Set a fixed value
  (e.g. 0.1 mm) to compare several parts on the same scale.
- Curvature also lights up every intended radius and bead; use it to see where the
  surface bends, and deviation to find defects.

### Why it differs from your CAE tool

Expect the colours and values to differ from the stamping simulation. That is not an
error in either tool - they measure different things:

| | STLSmooth defect map | Stamping simulation (CAE) |
|---|---|---|
| Compared against | A smoothed version of the part itself | The nominal die / CAD surface, or the solver's own criteria |
| Input | The exported STL only - often a re-meshed or simplified copy of the solver mesh | The full solver model: tool geometry, material, process |
| Defect definition | Local height above/below the smoothed shape, within the *Defect size* | Tool-specific criteria (e.g. stoning, curvature-based surface defects, springback vs nominal, thinning) |
| Depends on | Mesh density and the *Defect size* you choose - a different size gives different numbers | Solver settings and the criterion's own parameters |

So read the map as a pointer: a blue spot means "look here, the surface dips locally".
Confirm size and severity in the CAE tool. When presenting both side by side, say this
up front, so a different number in VRED isn't read as VRED being wrong.

Processing time: deviation takes about 1.7x a plain smooth of the same part, whatever the
Defect size; curvature about 1.1x (e.g. 180k triangles: smooth 2.3 s, deviation 3.9 s,
curvature 2.6 s).

## Settings

| Field | Default | Meaning |
|---|---|---|
| Crease angle | 40 deg | Faces meeting at more than this angle keep a hard edge. Raise to smooth more, lower to keep more edges. |
| Weld tolerance | auto | Vertices closer than this are merged. Auto = 0.01 % of the part's largest dimension. Increase if visible seams remain. |
| Subdivision | 0 | Phong subdivision passes after smoothing (VRED's own). Rounds off a faceted silhouette on coarse meshes. Each pass gives about 4x the triangles. |
| Keep original | on | Smooth an independent copy and leave the STL untouched. Off: replace the original in place. |
| Compare in a switch node | on | Put the original and all copies of a part in a switch `<part>_versions`, showing the newest. Off: copies next to the original, which is hidden. |
| Defect: Mode | Local deviation | Local deviation (approx. mm) or Curvature |
| Defect: Defect size | 20 mm | Deviation mode: largest shape counted as a defect |
| Defect: Colour range | auto | Deviation: value at full blue/red, +/- mm. Curvature: smallest bending radius (mm) at full red |
| Defect: Label maps as orientative in the scene | on | Adds a VRED annotation to each map saying it is an orientative estimate, not a CAE result. It follows the map's visibility, so it shows only when that version is shown. Delete it in the Annotations module for clean renders |

## Smooth shading, not new geometry

Smoothing fixes how the surface is lit; it does not add detail. On a coarse mesh the
outline (silhouette) still shows polygon edges - use Subdivision 1-2 for that. The
geometry stays the exact simulation result: vertex positions are not moved.

## Troubleshooting

| Symptom | Cause |
|---|---|
| No STLSmooth entry under Scripts | Python sandbox still enabled, or VRED not restarted after install |
| Still no entry after that | Double-nested folder (`STLSmooth\STLSmooth\`), or wrong VRED version folder. Check **Scripts > Terminal** for errors |
| Smoothed part disappears / original shows instead | Check which child the `<part>_versions` switch shows. Without a switch: original and copy overlap - check that the copy is visible and the original hidden |
| Part still looks faceted | Crease angle too low for that part - raise it and run Smooth selected again |
| Thin cracks/seams on the surface | Vertices not merged - raise Weld tolerance |
| Small features look rounded off or melted | Weld tolerance too high, or crease angle too high |
| Dark patches on part of the surface | Log shows "WARNING ... could not be made consistent" - that area of the mesh can't be oriented consistently (e.g. overlapping or twisted faces); re-export from the source software |
| Whole part looks dark / lit from behind | The export is inside-out - flip normals in VRED, or make the material two-sided |
| Log shows many "separate patches" | Parts of the mesh don't share vertices - raise Weld tolerance |
| Defect map shows plain white/grey | `STLSmooth_ramp.png` is missing next to the plugin, or VRED could not load it - check the log for "texture" messages. Running the button again re-applies the images to the existing material |
| Defect map is red/blue along every radius and wall | The part's features are as small as the defect size - lower Defect size, or use it on larger panels |
| Defect map button seems to do nothing | Read the log: "Skipped ... result copies" means only `_defect_` copies were selected - select the original or its `_smooth_` copy. Nothing in the log at all: check **Scripts > Terminal** and send the error |
| Log shows many non-manifold edges | The exported mesh itself has overlapping/duplicated faces - re-export from the source software |
| Import works but nothing gets smoothed | Select the imported nodes and use Smooth selected; the log line "Import done" should show new nodes |

## Disclaimer

Not a product of Autodesk, Inc. Not developed, endorsed, supported, maintained or warranted
by Autodesk, and not covered by any Autodesk support entitlement. Provided "as is", without
warranty of any kind. See `DISCLAIMER.txt` for the full text, including what the tool
changes in your VRED scene.
