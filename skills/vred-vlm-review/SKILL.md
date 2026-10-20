---
name: vred-vlm-review
description: Build an AI design-review copilot on top of Autodesk VRED — an in-VRED capture trigger plus an external Python worker that sends the rendered view to a vision-language model and returns a critique as a carousel card and an in-scene HUD. Use when the task mentions VRED plus a VLM/LLM, design review, critique of a render, perception-driven feedback, camera-settle capture, variant-set triggers, sceneplates/frontplates as HUD, or an Ollama/NVIDIA NIM/Claude vision backend.
---

# VRED + VLM design-review copilot

A working pattern for putting a vision-language model next to a designer in VRED: the
model reacts to *what is on screen* rather than to a typed prompt. Established by
building the thing; several items contradict what a first attempt would look like.

For exact API signatures and enum spellings, query the `vred-python-api` skill
(`py vredapi.py find …`) rather than guessing. For VRED panel/plugin UI, see
`vred-script-plugin`.

## Shape of the system

Two processes, one shared folder. Nothing links them but files.

```
VRED (Script Editor, embedded Python)     External worker (normal venv)
  capture_settle.py                         watches the drop folder
    vrTimer detects camera settle,          grabs the on-screen pixels (OS-level)
    or a variant set being applied          sends the frame to a VLM
    -> writes frame_0007.json               -> frame_0007.result.json
       {stem, matrix, event, t}             -> frame_0007_card.jpg  (carousel slide)
  writeback.py
    vrTimer polls *.result.json
    -> text frontplate HUD + Terminal
```

Shared drop folder (e.g. `C:\vred_ai\drop`) set identically in both halves.

**Why file-drop and not an in-process call:** VRED's embedded interpreter should not
block on a 2–5 s network round trip, and the worker needs libraries (`mss`,
`pygetwindow`, `openai`, `anthropic`, PIL) you do not want to install into VRED. The
trigger file also carries *why* the frame was captured, which the prompt uses.

**Why event-driven stills and not video:** VLM inference latency is the bottleneck. One
well-composed frame from a settled camera beats a stream of motion-blurred ones —
cheaper, higher quality, simpler.

## Capture: never re-render inside VRED

Do **not** use `vrMovieExport.createSnapshot` / `createSnapshotFast*` to feed the model.
They re-render (~2 s), take over the viewport and freeze navigation — fatal in a live VR
review. The VRED side writes only a trigger plus camera pose; the worker grabs the
already-rendered pixels from outside:

```python
import mss, pygetwindow as gw
from PIL import Image

def grab_vred(png_path, window_match="Autodesk VRED"):
    """OS-level grab of the VRED main window - no re-render, no UI lock."""
    cands = [w for w in gw.getAllWindows()
             if window_match.lower() in w.title.lower() and w.visible and w.width > 200]
    if not cands:
        raise RuntimeError(f"no visible window matching '{window_match}' - is VRED open?")
    w = max(cands, key=lambda x: x.width * x.height)   # main window = largest match
    try:
        if w.isMinimized:
            w.restore()
        w.activate()                                   # front, so nothing occludes it
    except Exception:
        pass
    region = {"left": w.left, "top": w.top, "width": w.width, "height": w.height}
    with mss.MSS() as sct:
        shot = sct.grab(region)
    Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX").save(png_path)
    return png_path
```

Match the window title specifically (`"Autodesk VRED"`, not `"VRED"`) so the Script
Editor and Terminal windows don't win, and pick the largest match as the main window.

## Use `vrTimer`, not `addLoop`

`addLoop` starves VRED's UI thread. Everything periodic on the VRED side — the settle
detector, the result poller — belongs on a `vrTimer`:

```python
timer = vrTimer(1.0 / 10)        # interval in SECONDS, so 10 Hz
timer.connect(watcher.tick)
timer.setActive(True)
# to stop:  timer.setActive(False)
```

10 Hz is plenty for settle detection, 4 Hz for polling results.

## Camera settle detection

Poll the active camera's world matrix, call it "still" when the frame-to-frame delta
falls below a threshold, and fire once per settle:

```python
def camera_matrix():
    cam = vrCameraService.getActiveCamera()   # vrdCameraNode (v2)
    m = cam.getWorldTransform()               # QMatrix4x4
    out = []
    for c in range(4):                        # .column(i) -> QVector4D
        v = m.column(c)
        out.extend([v.x(), v.y(), v.z(), v.w()])
    return out
```

`getWorldTransform()` returns a `QMatrix4x4` on the v2 API (`vrdNode.getWorldTransform`),
but the v1 `vrNodePtr.getWorldTransform()` returns a flat list of floats. Read column
vectors rather than indexing, and flatten defensively if the code may run against either.

Three parameters carry the behaviour, and all three want tuning per scene:
`DELTA_EPS` (sum-of-abs matrix difference below which the camera counts as still),
`SETTLE_SECONDS` (how long it must stay still), and `COOLDOWN` (minimum seconds between
captures). **Arm/disarm rather than re-firing:** set a flag on capture, clear it on the
next real movement, so a parked camera produces one frame and not a stream.

Route every trigger source through one `write_trigger(event, matrix)` function that owns
the cooldown — otherwise the settle detector and the variant-set hook double-fire on the
same moment. The `event` string travels to the worker, so the prompt can say *why* this
frame appeared.

## Variant-set triggers

Prefer the real signal. `vrVariantService.variantSetExecuted(variantSetNode)` fires on
every variant set execution and hands you the node — no authored scripts, no probing:

```python
vrVariantService.variantSetExecuted.connect(lambda node: fire_vset(node.getName()))
```

The legacy flat `vrVariantSets` module (v1) exposes no such signal, which is what leads
people to build discovery hacks. If you are stuck on a build where the v2 signal isn't
available, the layered fallback that works is: probe candidate signal names and connect
the first that exists; monkeypatch `vrVariantSets.selectVariantSet` to catch
script-driven changes; and expose a manual `fire_vset("name")` for a button or hotkey.
Log at startup which strategies actually armed — a UI click bypasses everything except a
real signal, and silence is indistinguishable from success.

`py vredapi.py class vrVariantService` lists signals alongside methods; a `find` for
`activated|changed` misses them because the name is `variantSetExecuted`.

## Text frontplate as an in-scene HUD

Feedback has to appear where the designer is looking — in the headset, not in a panel.
A **frontplate** sceneplate is a screen-space overlay composited over the render:

```python
root = vrSceneplateService.getRootNode()
node = vrSceneplateService.createNode(root, vrSceneplateTypes.NodeType.Frontplate, "AI Assistant")
plate = vrdSceneplateNode(node)
plate.setContentType(vrSceneplateTypes.ContentType.Text)
plate.setText(text)
```

Create the plate **once** and update it in place; creating one per result piles up
sceneplates in the scene. Reuse by name with `vrSceneplateService.findNode(name)`.

The styling setters are where the guessing goes wrong — these are the documented shapes:

| Setter | Takes | Not |
| --- | --- | --- |
| `setPosition(position)` | `vrSceneplateTypes.Position` enum — `TopLeft`, `Top`, `Center`, `BottomRight`, … | two floats / viewport fractions |
| `setOffset(offset)` | `QVector2D`, interpreted per `setOffsetMode(vrSceneplateTypes.SizeType.Absolute\|Relative)` | — |
| `setSize(size)` | sized per `setSizeMode(SizeType)` — `Absolute` is pixels | fractions by default |
| `setFontHeight(h)` | **integer pixels** per text line | a 0..1 fraction |
| `setFontColor(color)` | `QVector3D` | four RGBA floats |
| `setBackgroundColor(color)` | `QVector3D` | four RGBA floats |
| `setBackgroundTransparency(t)` | `float` — transparency is its own call | an alpha channel on the colour |

Note also `vrSceneplateTypes.NodeType.Frontplate`, not `vrSceneplateTypes.Frontplate`.

Wrap optional setters in a `_try(obj, method, *args)` helper that skips missing
attributes and swallows failures, so a styling call that varies by build cannot stop the
text from appearing — and **always keep the Terminal `print()` fallback**. On a headset,
a plate that silently failed to create is indistinguishable from a model that returned
nothing.

## The VLM backend: one env var, one config table

Every backend except Claude's native SDK is OpenAI-compatible, so only `base_url`,
`model` and `api_key` change. Select with a single environment variable and give each
deployment a launcher that sets it, rather than editing source:

```python
BACKEND = os.environ.get("VRED_BACKEND", "nim_cloud")

CONFIG = {
    "nim_cloud": dict(                                    # hosted NVIDIA NIM
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ.get("NVIDIA_API_KEY", ""),
        model="meta/llama-3.2-90b-vision-instruct"),
    "nim_local": dict(                                    # NIM container, own GPU
        base_url="http://localhost:8000/v1", api_key="not-needed",
        model="meta/llama-3.2-11b-vision-instruct"),
    "ollama": dict(                                       # easiest fully-local
        base_url="http://localhost:11434/v1", api_key="ollama",
        model="qwen2.5vl"),
    "vllm": dict(
        base_url="http://localhost:8000/v1", api_key="not-needed",
        model="Qwen/Qwen2-VL-7B-Instruct"),
    "claude": dict(                                       # native Anthropic SDK
        base_url=None, api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        model="claude-opus-5"),
}
CFG = CONFIG[BACKEND]
```

A launcher module that sets `os.environ["VRED_BACKEND"]` *before* importing the worker
keeps one copy of the capture/analyse/overlay logic and no branching at the call site.

### Local VLM gotchas

- **Not `llama3.2-vision` under Ollama.** Its `mllama` architecture is unsupported by
  llama.cpp — `unknown model architecture: 'mllama'`. Use **`qwen2.5vl`** (or `llava`,
  `minicpm-v`). The cloud NIM backend runs llama-3.2-90b-vision fine; this is a
  llama.cpp limitation, not a model one.
- **Don't run `ollama serve` on Windows.** It autostarts as a tray service, so the
  command fails with "address already in use" and sends you debugging a non-problem.
- **Preload the model** so the first critique isn't a cold start: POST an empty prompt to
  Ollama's native `/api/generate` (strip the `/v1` off the OpenAI-compatible base URL)
  with `keep_alive: -1` to pin it in VRAM, and register an `atexit` hook that posts
  `keep_alive: 0` to free it.

### Claude's image block differs from OpenAI's

OpenAI-compatible: `{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,…"}}`.
Anthropic native: a separate block type, raw base64 with **no `data:` prefix**, an
explicit `media_type` that must match the encoder, and `system` as a top-level argument
rather than a message:

```python
resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=800,
    system=SYSTEM + "\n" + SCHEMA,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": f"Critique this VRED render. {context}"},
        {"type": "image", "source": {
            "type": "base64", "media_type": "image/jpeg", "data": b64_jpeg}},
    ]}],
)
return resp.content[0].text
```

### Keep the payload small

Downscale and re-encode as JPEG before base64 — NVIDIA's inline image limit is around
180 KB, and a raw 4K PNG blows past it:

```python
def to_small_jpeg_b64(png_path, max_side=1024, quality=80):
    im = Image.open(png_path).convert("RGB")
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode()
```

## Prompt: collaborator, not critic

The prompt is the product. Two rules earn their keep:

**Make it prove it can see.** A `seeing` field that names the object, camera angle,
setting and one or two visible materials is what convinces a designer the feedback is
about *their* view and not generic advice. It also exposes a model that is hallucinating.

**Never invent faults.** Ask for what already works, then *at most* three optional
refinements phrased as offers ("you could", "consider", "try"), and explicitly allow
zero. A model told to critique will always find something wrong, which reads as noise.

Cap every phrase in words — the output has to fit an on-screen card and a HUD, and length
limits in the prompt are far more reliable than truncating afterwards.

```
{ "seeing":      str,                       # <=18 words; object, angle, setting, materials
  "strengths":   [str],                     # 1-2; never invent faults
  "suggestions": [{idea, area, why}],       # 0-3 OPTIONAL; area drives the card colour
  "next_steps":  [str] }                    # 1-3 forward-looking ideas
```

Ask for "ONLY valid JSON, no markdown, no prose" and still parse defensively — regex out
the first `{...}` block when `json.loads` fails, and return a structured error rather
than raising:

```python
def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else {"error": "unparseable", "raw": text}
```

The schema is a contract across four files (prompt, card renderer, VRED writeback,
dedup). Renaming a field means touching all of them — keep the list written down.

## Stop the model repeating itself

Across many camera angles of one model, a VLM converges on the same three suggestions.
Two mechanisms together fix it:

**A similarity gate.** Flatten each critique to comparable text and skip it if it is too
close to the last one *surfaced* (not the last one generated):

```python
SIM_THRESHOLD = 0.82

def too_similar(a, b):
    return bool(a) and bool(b) and difflib.SequenceMatcher(None, a, b).ratio() >= SIM_THRESHOLD
```

**Short-term memory in the prompt.** Feed the last ~10 ideas back as "you have ALREADY
suggested […] — do not repeat these or minor rewordings; if you have nothing materially
new for this angle, return `suggestions: []`". Permission to say nothing is what stops
the padding.

**Let variant-set frames and errors bypass the gate.** A variant change is a deliberate
act by the user; suppressing its feedback as "too similar" makes the tool look broken.
Also add the event to the prompt context — for a `vset` frame the camera did not move, so
tell the model to focus on materials, colour, finish and mood rather than framing.

Raise `temperature` a little (0.5 rather than 0.2) for variety across views; the schema
keeps the output disciplined.

## Card rendering

Compositing the render plus a suggestions panel into one JPEG gives a carousel slide that
survives the session, which is what people actually share afterwards.

**Word-wrap or it clips.** Fixed line spacing with model-generated text overlaps and runs
off the bottom. Wrap greedily against `ImageDraw.textlength`, advance `y` per drawn line,
and bound every section against a `bottom` value:

```python
def _wrap(d, text, font, max_w):
    words, lines, cur = (text or "").split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if not cur or d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines
```

Colour-code the `area` field (lighting / materials / reflections / framing / staging /
color / mood) with a swatch per suggestion — it makes a dense card scannable at a glance.
Fall back to `ImageFont.load_default()` when `arialbd.ttf` isn't present so the card
still renders on a machine without the font.

## Cleanup on stop

The drop folder grows without bound across sessions. Clear the working files on exit but
**keep the cards** — those are the output worth having:

```python
def cleanup_drop():
    """Clear working files (*.png snapshots, *.json poses and critiques);
    KEEP *_card.jpg carousel slides."""
    for f in glob.glob(os.path.join(DROP, "*.png")) + glob.glob(os.path.join(DROP, "*.json")):
        try:
            os.remove(f)
        except OSError:
            pass
```

Put it in a `try/finally` around the main loop so Ctrl-C runs it. It will **not** run on
window close or `taskkill` — say so in the README, because a user who closes the window
comes back to a folder full of PNGs and concludes the cleanup is broken.

## Patterns worth carrying elsewhere

- OpenAI-compatible backend abstraction: swap cloud/local by changing only
  `base_url`/`model`/`api_key`, and select with one environment variable.
- Event-driven capture: a settle detector plus a single shared-cooldown trigger function,
  so multiple sources can't double-fire.
- `difflib.SequenceMatcher` dedup gate combined with a short "already said" list fed back
  to the model — neither alone stops LLM repetition.
- PIL word-wrap with a bottom bound for any generated-text overlay.
- Defensive third-party API use: probe candidate names, `try/except` with log-once, and
  always keep a guaranteed fallback path (Terminal print, manual trigger).

## Machine note

Use `py`, never `python`/`python3` (Store stub). `py -m pip`, not `pip`.
