# Sound Emitter

A short snippet that **plays a sound file from a variant set** — useful for triggering an
engine sound, a door chime or any other audio cue as part of a variant.

*Community script. Not an Autodesk product — not developed, endorsed or supported by
Autodesk.*

## What's in this folder

| File | Purpose |
| --- | --- |
| `SoundEmitter.py` | The snippet, in both a VRED 2024+ and a VRED 2023 form. |
| `README.md` | This document. |

## Use

1. Add a **sound node** to your scene and note its name. The snippet assumes
   `Engine_sound` — change it to match yours.
2. Open the variant set that should trigger the sound, and find its **Script** field.
3. Paste in the block matching your VRED version, and replace
   `ADD_YOUR_FILE_PATH_HERE` with the full path to your audio file.

The sound then plays whenever that variant set is executed.

## Which block to use

The API changed, so pick the one for your release:

**VRED 2024 and newer** — the v2 API, with a dedicated sound file method:

```python
sound = vrNodeService.findNode("Engine_sound")
filename = r"ADD_YOUR_FILE_PATH_HERE"
sound.setSoundFile(filename)
sound.start()
```

**VRED 2023** — the older v1 API, setting fields directly:

```python
sound = findNode("Engine_sound")
filename = 'ADD_YOUR_FILE_PATH_HERE'
sound.setFieldString("soundFile", filename)
sound.setFieldBool("play", true)
```

Use one or the other, not both.

## Notes

- Keep the `r"..."` prefix on the Windows path in the 2024+ version. Without it a
  backslash in the path is read as an escape character and the file won't be found.
- The node name must match a real sound node in the scene, otherwise `findNode` returns
  nothing and the snippet fails silently.
