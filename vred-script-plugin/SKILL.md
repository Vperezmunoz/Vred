---
name: vred-script-plugin
description: Build, install, debug or test an Autodesk VRED Python script plugin — panels under the Scripts menu, PySide6 UI, materials, and Web Engine video/HTML textures. Use when the task mentions VRED script plugins, ScriptPlugins, vrWebEngineService, vrMaterialService, vrNodeService, VREDPluginWidget, a VRED panel that won't appear, or putting video/web content on a mesh in VRED.
---

# VRED script plugins

For exact API signatures, enum spellings and shipped example scripts, query the
`vred-python-api` skill (`py vredapi.py find …`) instead of guessing — this page only
covers the behaviour the reference docs get wrong. For screen-space HUD overlays
(sceneplates), external frame capture, or wiring a vision model to the live view, see
`vred-vlm-review`.

Working knowledge for VRED 19.x (PySide6-era). Several items below contradict Autodesk's
own documentation — they were established by trial against a real VRED build, so trust them
over the docs.

## Layout and loading

```
Documents\Autodesk\VRED-<version>\ScriptPlugins\
    MyPlugin\
        vrMyPlugin.py        <- module name is "vr" + folder name
        <any support files>
```

- The **folder name becomes the menu entry**: `Scripts ▸ MyPlugin`.
- **`Documents` may be redirected to OneDrive.** On a managed corporate machine the real
  path is `%USERPROFILE%\OneDrive - <Company>\Documents\Autodesk\...`, and
  `C:\Users\<user>\Documents` may not exist at all. Creating the literal
  `Documents\Autodesk\...` path silently produces a second, non-synced tree that VRED
  never reads. Check which one exists before writing anything.
- Keep the `vr<FolderName>.py` naming. It is the convention that demonstrably loads; don't
  experiment with alternatives inside a deliverable a customer will install.
- The folder must sit *directly* in `ScriptPlugins`. Unzipping carelessly produces
  `ScriptPlugins\MyPlugin\MyPlugin\`, which never loads.
- **VRED's Python sandbox must be disabled** (Edit ▸ Preferences, Python/script settings)
  or script plugins are not loaded at all. Restart VRED afterwards. This is the single most
  common reason a panel "doesn't appear", and it is silent — no error, no menu entry.
- A plugin that raises at import is dropped silently too. Check **Scripts ▸ Terminal**.

## The host-widget pattern

VRED injects a `VREDPluginWidget` into the plugin namespace and the panel must instantiate
itself at import time. Guard only the *name lookup*, so that real errors inside the panel
still surface instead of leaving VRED with a silently missing plugin:

```python
try:
    _host = VREDPluginWidget
except NameError:
    _host = None       # running outside VRED - a syntax check, or an editor

if _host is not None:
    myPanel = MyPanel(_host)
```

In `__init__`, attach to the host's layout, creating one if absent:

```python
if parent is not None:
    layout = parent.layout() or QtWidgets.QVBoxLayout(parent)
    layout.addWidget(self)
```

## API imports

VRED injects its services as bare names, but importing types explicitly lets an editor
resolve them and costs nothing:

```python
try:
    from vrKernelServices import vrdWebEngine, vrMaterialTypes, vrTextureTypes
except ImportError:
    pass
```

**v2 services are injected as bare names; v1 modules are not.** `vrHMDService`,
`vrVariantService`, `vrFileIOService` and friends are already in the namespace, but
`vrOSGWidget`, `vrController` and the rest of the legacy flat API must be imported:

```python
import vrOSGWidget      # NameError without this, however "global" it looks
```

This is the trap behind a plugin that runs but reports nothing: `vrOSGWidget.getFPS()`
inside a `try/except` raises `NameError`, the handler returns a default, and you get a
panel full of `0.0` with no error anywhere. Autodesk's own Innoactive plugin imports
`vrOSGWidget` / `vrController` explicitly while using `vrCameraService` bare — that split
is the rule, not a style choice.

**Never write a bare `except` that returns a default from a VRED call.** Report the
exception the first time it happens and return a sentinel the UI can render as `n/a`:

```python
def read_fps():
    try:
        return float(vrOSGWidget.getFPS())
    except Exception as exc:
        _report("getFPS", exc)   # print once to the terminal, show in the panel
        return None
```

A silently-swallowed `NameError` is indistinguishable from a genuine zero, and in a VR
tool you only find out after putting the headset on. Give any panel a **live readout of
the raw values it is reading** (frame rate, render mode, whether the HMD is active). It
turns "the numbers are wrong" into a one-glance diagnosis without entering VR.

## Gotchas that cost real time

**`setTexture`, not `setTextureSlot`.** Autodesk's own `class_vrWebEngineService` example
uses `setTextureSlot()`; it does not exist in any VRED build.
```python
engine.setTexture(vrdWebEngine.TextureSlotType.DiffuseAndIncandescence)
```

**`QUrl.toEncoded()`, not `toString()`.** `toString()` returns the "pretty" form with
percent-escapes decoded, so a path containing spaces (e.g. a synced `OneDrive - CompanyName` folder) comes back with raw spaces.
VRED stores that happily and `getUrl()` echoes it back unchanged — but Chromium cannot
resolve it, the page never loads, and the surface renders as bare material with no error.
```python
url = bytes(QtCore.QUrl.fromLocalFile(html).toEncoded()).decode("ascii")
```

**Create a v2 material; don't reuse what the node hands back.** `vrdUiEngine.setMaterial()`
rejects the v1 `vrMaterialPtr` that `node.getMaterial()` can return on older geometry. Use
`vrMaterialService.createMaterial(name, vrMaterialTypes.Phong)` /
`findMaterial(name)` and `applyMaterialToNodes(mat, nodes)`.

**Colours want `QVector3D`,** not tuples — `setDiffuseColor`, `Incandescence.setColor`.

**`QVector3D` has no copy-constructor overload in this VRED's bundled PySide6.**
`QtGui.QVector3D(other_vector)` raises `TypeError: called with wrong argument types`. Build
from components: `QtGui.QVector3D(v.x(), v.y(), v.z())`.

**VRED does not tick "Use Texture" for you.** After assigning, set
`tex.setUseTexture(True)` on both the diffuse and incandescence textures, and
`setMappingType(vrTextureTypes.MappingType.UVMapping)` where supported — Web Engine
interaction only worked with UV mapping for most of this API's life.

**A diffuse texture is modulated by the base colour.** A grey base shows grey video. Set
base colour and incandescence colour to white and drive brightness with incandescence
intensity instead.

**No verified selection-changed signal.** Poll `vrNodeService.getSelectedNodes()` on a
`QtCore.QTimer` (750 ms is fine — it's one cheap call).

**In a Script Editor script, poll with `vrTimer`, not `addLoop`.** `addLoop` starves
VRED's UI thread. `vrTimer` takes its interval in *seconds* — `vrTimer(1.0 / 10)` for
10 Hz — and needs `setActive(True)` before it runs.

```python
timer = vrTimer(1.0 / 10)
timer.connect(watcher.tick)
timer.setActive(True)          # to stop: timer.setActive(False)
```

A plugin panel is already inside Qt's event loop, so use `QtCore.QTimer` there; `vrTimer`
is for the Terminal and Script Editor, where there is no widget to hang a timer off.

**A script plugin's module is not importable from other VRED script scopes.** A variant
set's Script field, or the Terminal, cannot rely on `import vrMyPlugin` finding your
module. Publish the entry points into `builtins` at import time and call them bare:

```python
import builtins
builtins.vredFpsSetContext = set_context   # variant set script: vredFpsSetContext("Interior")
```

**Prefer a real signal over asking the user to embed a script.** Before designing around
"the user pastes a line into each variant set", search the API for the event —
`vrVariantService.variantSetExecuted(variantSetNode)` fires on every variant set
execution and hands you the node, so context tracking needs no authored scripts at all.
`py vredapi.py class <Service>` lists signals alongside methods; a targeted `find` for
`activated|changed` often misses them.

**Reuse engines and materials by name** rather than piling up duplicates on every run:
check `getWebEngine(name)` / `findMaterial(name)` first.

## Web Engine video: the autoplay wall

Chromium refuses to start a video without a user gesture, and VRED's Web Engine keeps
`PlaybackRequiresUserGesture` on. `muted` is necessary but **not** sufficient. Two ways
through, and you need one:

1. `vrWebEngineService.setInteractionEnabled(True)`, then the user clicks the mesh once —
   a real click is the gesture Chromium wants.
2. Launch VRED with `QTWEBENGINE_CHROMIUM_FLAGS=--autoplay-policy=no-user-gesture-required`
   in the environment. Detect it with
   `"no-user-gesture-required" in os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")` and
   drop the "click the mesh" hint from your UI when it's set.

Retry `play()` on a timer rather than once on `canplay` — a gesture-blocked page has to keep
trying until something lets it through.

**Codec: VP9 only.** VRED's embedded Chromium has no H.264. An MP4 will not play in a Web
Engine; convert to VP9/WebM (audio: Opus). See the `ffmpeg-packaging` skill if you need to
ship the encoder.

**Make failure visible on the texture.** On a mesh, a page that failed silently is
indistinguishable from one that never loaded. Overlay a large status div for
`error` / `stalled` / autoplay-blocked, and echo detail back to VRED's terminal:
```javascript
if (window.vred && vred.executePython) {
  vred.executePython("print('[webengine] " + String(msg).replace(/'/g, '') + "')");
}
```

## Measuring VR performance

- **Frame rate:** `vrOSGWidget.getFPS()` / `getAverageFPS()` (v1 — import the module).
  `getAverageFPS()` averages since VRED launched, not since your session began, so build
  your own accumulator sampling `getFPS()` on a `QtCore.QTimer` (250 ms) if you want a
  per-session figure.
- **Session boundaries:** `vrHMDService.isHmdActive()` and the
  `hmdStatusChanged(active)` signal; `vrImmersiveInteractionService` exposes both under
  the same names. This covers OpenXR headsets driven by third-party runtimes (Innoactive
  Spatial Runtime, Apple Vision Pro) — nothing plugin-specific is needed.
- **DLSS:** `vrOSGWidget.getDLSSQuality()` returns one of the module constants
  `VR_DLSS_OFF / _PERFORMANCE / _BALANCED / _QUALITY / _ULTRA_PERFORMANCE / _DLAA`, gated
  by `isDLSSSupported()`. The numeric values aren't documented — resolve them off the
  module with `getattr(vrOSGWidget, "VR_DLSS_QUALITY", None)` rather than hardcoding, and
  don't collapse the mode to a bool if you want to tell Quality from Performance.
- **Which renderer is active** takes two calls, and there is no `getRenderMode()`.
  `vrOSGWidget.getRaytracingEnabled()` picks the pair, then the mode index names it —
  the inverse of the shipped `examples/snippets/setRenderer` script
  (`py vredapi.py example snippets_setRenderer`), which is the only place this mapping is
  written down:

  ```python
  if vrOSGWidget.getRaytracingEnabled():
      mode = vrRenderSettings.getRaytracingMode()      # 0 CPU, 1 GPU raytracing
  else:
      mode = vrRenderSettings.getRasterizationMode()   # 0 OpenGL, 1 Vulkan
  ```

  `vrRenderSettings` is another v1 module — import it.
- **Vulkan raytracing toggles** hang off `vrRenderSettingsService.getSettings()`:
  `getUseRaytracedReflections() -> bool`, and `getRealtimeEnvironmentShadowsMode()`
  returning `vrRenderSettingsTypes.RealtimeEnvironmentShadowsMode`
  (`Off`, `ScreenSpaceAmbientOcclusion`, `RaytracedAmbientOcclusion`,
  `RaytracedEnvironmentShadows`, `RaytracedDiffuseGI`). Only the `Raytraced*` values need
  Vulkan; SSAO also applies under OpenGL. Both readings are meaningless while a raytracing
  renderer is active — gate on the engine and report `n/a` rather than a stale `Off`.
- **Hardware, for attributing a benchmark:** `vrGPUService.gpuInfo()` (`getName()`),
  `gpuStateInfo()` (total/free/used MB, usage %, temperature), `openGLInfo()` (vendor,
  renderer, GL version, driver version as an int list) and `raytracingInfo()`
  (`isGPURTSupported()`). VRED's own build is `vrController.getVredVersion()` /
  `getVredVersionYear()` — a v1 module again. For the headset,
  `vrHMDService.getActiveOpenXRRuntimeName()` / `getActiveOpenXRSystemName()` name the
  runtime and device ("Innoactive Spatial Runtime" / "Apple Vision Pro"). CPU and RAM have
  no VRED API: use `platform`, `os.cpu_count()` and `ctypes` `GlobalMemoryStatusEx`
  instead of adding a `psutil` dependency.
- **No OpenXR frame timings.** `vrOpenVRFrameTimings` (dropped frames, reprojection,
  GPU/CPU split) is OpenVR-only; there is no OpenXR equivalent, so an OpenXR headset gives
  you frame rate and nothing deeper.
- **VRED's own benchmark CSV:** `vrOSGWidget.startStatisticsRecording(index)` /
  `stopStatisticsRecording` / `writeRecordedStatistics(index, folder)` (`index=-1` is the
  focused window) — worth reaching for when `getFPS()` isn't enough.

### Analyzing a custom FPS logger's tab-separated output

A logger built around the calls above (columns: Timestamp, Context, Engine, DLSS,
RT Reflections, Env Shadows, Avg/Min/Max FPS, Duration, Samples) has recurring shapes
worth checking before charting it:

- **First row is often `Context = Unknown`.** It's the sample taken before the first
  context switch fires — discard it, don't average it in.
- **The same settings combo gets logged more than once** in one session (repeat runs,
  or a context revisited later). Average duplicate rows for the same
  Context/DLSS/RT-Reflections/Env-Shadows combo into one value rather than charting
  each run as its own bar.
- **The Env Shadows label can drift between sessions** (e.g. `SSAO` vs plain `Off` for
  the disabled state) — normalize before joining logs from different sessions, or a
  chart silently splits one state into two.
- **A log can be missing entire combos** that a same-resolution session logged
  elsewhere. If a complete grid is required anyway, infer the missing cell as that
  table's own overall average and mark it clearly (hatch/asterisk + tooltip) — never
  silently backfill a number that looks as trustworthy as a measured one.

## Lights are two independent node graphs, not one

A VRED light is one logical entity but exposes **two separate `vrdNode` hierarchies** with
independent parent/children: the main scene graph node (what the viewport, Scenegraph
panel, and `vrNodeService`/`vrScenegraphService` see) and the light-graph "module" node
(what the Light Editor and `vrLightService` see). Grouping, reparenting, or cloning one
does **not** affect the other — this is the root cause behind most "light vanished /
unselectable / not grouped" bugs.

```python
from vrKernelServices import vrdBaseLightNode

def is_light(node):
    return node.isType(vrdBaseLightNode)   # robust across either graph's handle

def to_scene_node(node):
    """A selection made in the Light Editor hands you the light-graph node. Scene graph
    ops (cloneNodes, createNode, getParent) need the scene graph node instead."""
    if not is_light(node):
        return node
    shared = node.getModuleNode().getSharedNodes()
    return shared[0] if shared else node
```

Symptoms this explains:
- Lights disappear from the render window and Scenegraph, remain only in the Light
  Editor, and neither the lights nor a light group built from them can be selected or
  zoomed to: scene-graph code was handed a light-graph node (or vice versa) and built a
  hierarchy in the wrong graph.
- A tool that dedupes a multi-select by `node.getPath()` double-counts a light selected in
  both the viewport and the Light Editor: key on the *light-graph* path
  (`node.getModuleNode().getPath()`) for anything typed as a light, not the raw handle's
  own path.
- Cloning a light from a Light-Editor selection produces a clone visible only in the Light
  Editor, not the Scenegraph: `vrScenegraphService.cloneNodes` clones within whatever graph
  the input node belongs to, so normalize with `to_scene_node()` before calling it.

## Linked (shared-data) copies vs independent duplicates

For "editing one copy should update all of them" (an array/grid of instances, not
independent duplicates), use `vrScenegraphService.cloneNodes(nodes)` with transformable
clone roots enabled, not `vrLightService.duplicateLights()` /
`vrScenegraphService.duplicateNodes()` (which produce fully independent, unlinked data).

```python
was = vrScenegraphService.getTransformableCloneRootEnabled()
vrScenegraphService.setTransformableCloneRootEnabled(True)   # each clone gets its own
try:                                                          # transform; data still shared
    clone = vrScenegraphService.cloneNodes([node])[0]
finally:
    vrScenegraphService.setTransformableCloneRootEnabled(was)
```

`setTransformableCloneRootEnabled` only works when the cloned node is a genuine
transform-root type (geometry qualifies). **A light node does not** — cloning it directly
still shares the transform too, so every "linked" clone collapses onto the same position.
Work around it by wrapping the light in a private carrier `TransformNode`, and cloning the
carrier instead — the light itself (child of the carrier) stays the one shared/linked
entity, while each carrier clone gets its own independent position:

```python
carrier = vrScenegraphService.createNode(vrScenegraphTypes.NodeType.TransformNode, parent, name)
carrier.children.append(light_scene_node)
# clone `carrier` per grid cell (with transformable clone roots enabled) and set
# translation on each carrier clone's own transform, not the light's.
```

Reparent nodes into a group with `group.children.append(node_or_list)` — `vrdNode.children`
is a mutable `vrdNodeList` property, not a method-only API.

## Batching several operations into one undo step

```python
vrUndoService.beginMultiCommand("Create Array")
try:
    ...  # any number of scene graph edits
finally:
    vrUndoService.endMultiCommand()
```

Wrap the whole loop, not each iteration — otherwise Ctrl+Z only undoes the last node.

## Long-running work

Never block VRED's UI thread. Run external tools with `QtCore.QProcess` and parse progress
from stdout. On Windows, pass `creationflags=subprocess.CREATE_NO_WINDOW` to any
`subprocess.run()` so console windows don't flash up behind VRED.

## Testing outside VRED

You can exercise everything except the VRED API calls by stubbing PySide6 — worth doing
before shipping, since the alternative is a manual VRED restart per iteration:

```python
import sys, types

def stub_pyside6():
    def ns(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        return m
    base = type("Stub", (object,), {})
    names = ("QWidget QLabel QPushButton QVBoxLayout QFormLayout QSpinBox "
             "QDoubleSpinBox QCheckBox QProgressBar QFileDialog").split()
    w = ns("PySide6.QtWidgets", **{n: type(n, (base,), {}) for n in names})
    c = ns("PySide6.QtCore", Qt=base, QTimer=base, QProcess=base, QUrl=base)
    g = ns("PySide6.QtGui", QVector3D=base)
    for n, m in (("PySide6", ns("PySide6", QtCore=c, QtGui=g, QtWidgets=w)),
                 ("PySide6.QtCore", c), ("PySide6.QtGui", g), ("PySide6.QtWidgets", w)):
        sys.modules[n] = m
```

Widget classes must be real classes (not mocks) because the panel subclasses `QWidget`.
The `VREDPluginWidget` guard above then leaves the module importable, so module-level
helpers — path discovery, config load/save, argument building, geometry maths — are
directly unit-testable.

Also assert that any HTML template fully substitutes: a leftover `__TOKEN__` is a silent
black screen, not an error.

## Machine note

On this machine use `py`, never `python`/`python3` (Store stub). `py -m pip`, not `pip`.
