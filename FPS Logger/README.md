# FPS Logger

A VRED script plugin that measures the **average frame rate of a VR session** and logs it
next to your scene, split by scenario and render settings so runs can be compared.

*Community script. Not an Autodesk product — not developed, endorsed or supported by
Autodesk, and not covered by any Autodesk support entitlement.*

Built for headset testing over OpenXR (developed against the Innoactive Spatial Runtime
with an Apple Vision Pro), but nothing in it is runtime-specific — any OpenXR HMD that
VRED reports as active will be measured.

## What's in this folder

| File | Purpose |
| --- | --- |
| `vrFpsLogger.py` | The plugin. This is the only file VRED needs. |
| `README.md` | This document. |

## Requirements

- VRED Professional. Developed and tested on **2027.1** (internal version 19.1).
- An OpenXR headset, for the VR measurements. The panel itself opens without one.
- Nothing else — no `pip install`, no third-party packages. Everything comes from the
  Python standard library and VRED's own API.

## Install

1. Copy the **`FPS Logger` folder's contents** into a folder named `FpsLogger` inside your
   VRED `ScriptPlugins` directory:

   ```
   Documents\Autodesk\VRED-<version>\ScriptPlugins\
       FpsLogger\
           vrFpsLogger.py
   ```

   - **Keep the file name `vrFpsLogger.py`.** VRED derives the module name from the folder
     name (`vr` + folder), so renaming either one stops it loading.
   - **Don't double-nest.** Unzipping carelessly produces
     `ScriptPlugins\FpsLogger\FpsLogger\vrFpsLogger.py`, which never loads.
   - If your `Documents` is redirected to OneDrive, use the redirected path — e.g.
     `C:\Users\<you>\OneDrive - <Company>\Documents\Autodesk\...`. A folder created under a
     plain `C:\Users\<you>\Documents` that VRED isn't using will silently do nothing.

2. **Disable VRED's Python sandbox**: `Edit > Preferences > Script Settings`. With the
   sandbox on, script plugins are not loaded at all — no error, no menu entry.

   > Security note: this is a VRED-wide setting. Once disabled, **every** Python script
   > VRED runs afterwards is unsandboxed, not just this one. Only do this on a machine
   > where you control which scenes and scripts you open.

3. Restart VRED. The panel appears under **`Scripts > FpsLogger`**.

## Use

1. Open the panel. The **live readout** shows what the plugin is reading right now —
   frame rate, renderer, DLSS mode, raytracing settings, and whether an HMD is active.
   Check it before putting a headset on; if a value shows `n/a` here, it will be wrong in
   a session too.
2. Press **Start** to arm.
3. Enter VR and use the scene normally. Measurement runs only while the headset is active.
4. Leave VR. The row appears in the table and is appended to the log file.
5. Repeat as often as you like — every VR session while armed produces its own row.
6. Press **Stop** when finished.

Arming and never entering VR writes nothing.

## Tagging scenarios with variant sets

The **Context** column follows your variant sets automatically. Executing a variant set
called `Interior` tags subsequent measurements as `Interior` — no script inside the
variant set is required; the plugin listens to VRED's `variantSetExecuted` signal.

If you want to set a context explicitly instead, call this from anywhere in VRED
(a variant set's Script field, or the Terminal) — no import needed:

```python
vredFpsSetContext("Interior")
```

## What splits a measurement

A running measurement is closed and a fresh one started whenever any of these change, so
an average is never blended across two different configurations:

- Context (variant set)
- Render engine — OpenGL, Vulkan, CPU Raytracing, GPU Raytracing
- DLSS mode — Off, Performance, Balanced, Quality, Ultra Performance, DLAA
- Raytraced reflections (Vulkan)
- Real-time environment shadows mode (Off, SSAO, Raytraced AO, Raytraced Env Shadows,
  Raytraced Diffuse GI)

This means you can change DLSS or flip to Vulkan without leaving VR and still get clean,
separately-averaged numbers for each.

## The log file

Written next to the current scene as `<scene name>_fps_log.txt`, tab-separated so it
pastes straight into Excel. If the scene has never been saved, it falls back to
`vred_fps_log.txt` in your home folder. Runs append, so the file accumulates.

Each armed run first writes a comment block identifying the machine, so results stay
attributable when you compare them later:

```
# Session started 2026-01-15 14:22:07
# VRED: 19.1 (2027)
# OS: Windows-11-10.0.26200-SP0
# CPU: Intel64 Family 6 Model 197 Stepping 2 (16 logical cores)
# RAM: 63.4 GB
# GPU 0: NVIDIA RTX 6000 Ada
# OpenGL: NVIDIA Corporation / RTX 6000 Ada (version 4.6, driver 576.88)
# GPU raytracing supported: True (driver 576.88)
# OpenXR: Innoactive Spatial Runtime / Apple Vision Pro
Timestamp	Context	Engine	DLSS	RT Reflections	Env Shadows	Avg FPS	Min	Max	Duration (s)	Samples
```

The plugin only ever writes this one file. It does not modify your scene.

## One thing it can't work around

The frame rate comes from VRED's own `getFPS()`, which reports the render window's rate.
There is no OpenXR frame-timing API exposed to VRED Python — `vrOpenVRFrameTimings`
(dropped frames, reprojection, GPU/CPU split) is OpenVR-only. So you get frame rate, and
nothing deeper, on an OpenXR headset.

If you need per-frame detail, VRED's built-in statistics recording
(`vrOSGWidget.startStatisticsRecording` / `writeRecordedStatistics`) writes a richer CSV.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| No `FpsLogger` entry under the Scripts menu | The Python sandbox is still enabled — see install step 2 — or VRED wasn't restarted. |
| Still no entry after disabling the sandbox | Folder is double-nested, the file was renamed, or it's under a `Documents` folder VRED isn't using (OneDrive redirection). |
| Menu entry exists but the panel is empty | The plugin raised while loading. Open `Scripts > Terminal` for the traceback. |
| A red error line in the panel | A VRED call failed; the message names it. This is deliberate — the plugin shows failures rather than logging plausible-looking zeros. |
| Live readout shows `FPS: n/a` | VRED isn't reporting a frame rate; check the Terminal for the reported error. |
| `RT Reflections` / `Env Shadows` show `n/a` | Expected — these are rasterizer settings and read `n/a` under CPU/GPU Raytracing. Reflections are Vulkan-only. |
| DLSS shows `DLSS Unsupported` | The GPU or driver doesn't support DLSS, as reported by VRED. |
| Table stays empty after a VR session | The plugin wasn't armed (press **Start** before entering VR), or the headset never registered as active — watch the `HMD:` field in the live readout. |
| Context column says `Unknown` | No variant set has been executed yet this session. Execute one, or call `vredFpsSetContext("...")`. |
| No log file next to the scene | An unsaved scene logs to `vred_fps_log.txt` in your home folder instead. The panel shows the path it used. |

## Disclaimer

This is a personal, community-contributed script. It is **not** an Autodesk product, is
not developed, endorsed, supported or warranted by Autodesk, and is not covered by any
Autodesk support entitlement. Provided as-is, without warranty of any kind, express or
implied. Use at your own risk.

Installing it requires disabling VRED's Python sandbox, which affects every script VRED
runs afterwards — see the security note in the install section.

No third-party dependencies are bundled; the plugin uses only the Python standard library
and VRED's own API.
