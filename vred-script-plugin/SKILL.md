---
name: vred-script-plugin
description: Build, install, debug or test an Autodesk VRED Python script plugin — panels under the Scripts menu, PySide6 UI, materials, and Web Engine video/HTML textures. Use when the task mentions VRED script plugins, ScriptPlugins, vrWebEngineService, vrMaterialService, vrNodeService, VREDPluginWidget, a VRED panel that won't appear, or putting video/web content on a mesh in VRED.
---

# VRED script plugins

For exact API signatures, enum spellings and shipped example scripts, query the
`vred-python-api` skill (`py vredapi.py find …`) instead of guessing — this page only
covers the behaviour the reference docs get wrong.

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

**VRED does not tick "Use Texture" for you.** After assigning, set
`tex.setUseTexture(True)` on both the diffuse and incandescence textures, and
`setMappingType(vrTextureTypes.MappingType.UVMapping)` where supported — Web Engine
interaction only worked with UV mapping for most of this API's life.

**A diffuse texture is modulated by the base colour.** A grey base shows grey video. Set
base colour and incandescence colour to white and drive brightness with incandescence
intensity instead.

**No verified selection-changed signal.** Poll `vrNodeService.getSelectedNodes()` on a
`QtCore.QTimer` (750 ms is fine — it's one cheap call).

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
