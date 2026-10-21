---
name: vred-physics-grab
description: Pinch-grab objects with tracked hands in Autodesk VRED XR, and start/stop scene physics without breaking VRED's own hand interaction. Use when a task mentions VRED physics in VR, vrPhysicsService, vrdPhysicsObjectNode, grabbing or moving physics objects with hands, pinch gestures, hand colliders, kinematic vs dynamic bodies, resetting objects that physics moved, or the PhysicsGrab plugin. It holds the finished, headset-verified plugin source, the behaviour of VRED's physics API that the docs do not state, and offline tests.
---

# Pinch-grab and scene physics start/stop in VRED XR (PhysicsGrab)

`plugin/PhysicsGrab/vrPhysicsGrab.py` is a working alpha, verified in a headset on
VRED 19.2 (2027.2) with hand tracking. **Start from this source; don't rebuild it.**
Installed copy: `OneDrive - Autodesk\Documents\Autodesk\VRED-19.2\ScriptPlugins\PhysicsGrab\`
(only 19.2 so far, by the user's choice). Panel: **Scripts > PhysicsGrab**, driven from the PC.

Why it exists: VRED runs physics whenever VR is on, because the hand interaction is built on
it, but the hand colliders are crude (a cylinder plus one index-tip collider) so customers
cannot really pick parts up. The alpha uses a kinematic attach on pinch instead of real
grasp physics. That sidesteps force, momentum and jitter issues completely.

## What the panel does

- **Stop / Start scene physics**: `setActive(False/True)` on each physics object,
  never `vrPhysicsService.setActive` / `setPaused` (the hands would stop working). Start also
  switches on every inactive **group** above a filtered object and wakes each object. An
  optional checkbox restores the state from before Stop instead of switching everything on.
- **Object filter / Exclude names** (default `collider, collision_geo`).
- **Pinch grab** (30 ms `QTimer`):
  1. pinch >= *Freeze* (0.30): the nearest grabbable object is taken out of the simulation,
     so closing fingers cannot push it away;
  2. pinch >= *Close* (0.80): grab; below *Release* (0.50): let go (hysteresis);
  3. while held, the object follows a frame with the **hand's rotation placed at the pinch
     point** (turns around the fingertips, not the wrist). Other modes: position only, or
     hand origin.
- **Capture home / Reset transforms** with automatic fallback (see below).
- Live readout (pinch strength per hand, frozen/holding), and a log that explains misses
  ("pinch found nothing: point …, nearest Box at 312 (radius 150)") and holds
  ("hold Box: 45 updates; hand moved 55, pinch moved 56, target moved 54, object moved 0").
  Those two lines located every bug below in one headset round each.

## VRED physics behaviour the docs don't tell you (all seen in VRED 19.2)

1. **Every physics object is named `PhysicsObject` and their `getPath()` values collide.**
   Keying anything by physics-object path merged all objects into one entry: the static
   shadow plane inherited a dynamic object's type and got grabbed, and Reset found 0 objects.
   Key by the scene node: `obj.getSceneNode().getObjectId()`; show `getSceneNode().getName()`.
2. **The editor tree is not the full list.** `vrPhysicsService.getDynamicObjects()` /
   `getKinematicObjects()` return scene nodes (11 dynamic / 8 kinematic in a 3-part test scene);
   map them with `getPhysicsObject(node)`. Use these lists as the authority on collider type.
3. **VRED's hand colliders are physics objects too**: `Collider`, `L_index_collision_geo`,
   `R_index_collision_geo`, reported as **Dynamic** and marked `isInternal()`. Exclude internal
   objects and those names from grab *and* from Stop, or the hand interaction breaks.
4. **A deactivated body still owns its node's pose.** `setWorldTransform` on the scene node of a
   `setActive(False)` object is silently ignored (45 updates, object moved 0). Moving it works
   once the object is **Kinematic and active**: a kinematic body follows its node, and the hand
   cannot push it. The plugin detects the stall after 5 updates, switches to kinematic and
   remembers that for later grabs; release restores the original type and wakes the object.
5. **Reset needs care for the same reason.** Plain "switch off, set node, switch on" did not
   move objects back in the first builds. `_place()` tries `reactivate`, then `rebuild`, then
   `kinematic drive` (kinematic, set, 200 ms, restore type), verifies each after ~0.3 s
   against a 20-unit tolerance, and keeps whichever worked. Reset works in VRED with this
   chain; which method succeeded was not recorded. The log line "placed OK with '...'" says,
   so note it here next time and drop the methods that never win.
6. **An inactive `vrdPhysicsGroupNode` deactivates all its children** whatever their own flag
   (stated in the docs, easy to miss): Start must switch groups on too.
7. **Re-activated objects can stay asleep** until touched. Call `setWakeCounter(0.4)` after
   `setActive(True)`.
8. Collider type values: `vrPhysicsTypes.ColliderType.Dynamic / Static / Kinematic`.

## Tracked hands (`vrDeviceService.getRight/LeftTrackedHand()` -> `vrdTrackedHand`)

- `isTracked()`, `getPinchStrength()` (0..1) and `getTransform()` (world pose, despite the docs
  calling it an "offset") all update live.
- `getJointTransform(vrHandTypes.FingerType.Thumb / Index, 4)` = fingertip. Multiplying it by
  `getTransform()` (joints relative to the hand) gave a pinch point about 10 mm from the hand
  origin and grabbing worked, so the "relative to hand" default is right, but the panel keeps
  a world-space and a hand-origin option in case another runtime differs.
- Scene units are mm; a 150 grab radius (to the object's world bounding box) works.
- Exclude static objects as candidates: a floor or shadow plane has a huge bounding box, so
  the pinch point is always "inside" it and it wins every time.

## PySide6 traps hit here (VRED's bundled build)

- **`QMatrix4x4(other)` raises TypeError** (no copy constructor, same as `QVector3D`). It
  silently killed every follow update. Build new matrices instead:
  `move = QMatrix4x4(); move.translate(d); target = move * start`.
- `QMatrix4x4.inverted()` may return the matrix or `(matrix, ok)`; handle both (`_inverse`).
- Don't write `value or fallback` for Qt value types; test `is None` (a zero vector is falsy).
- An exception in a timer slot only reaches Scripts > Terminal. Also log it in the panel
  (`tick failed: …`), once per distinct message, or it looks like "nothing happens".

## Tests

```
py -I tests\test_grab.py        # grab, freeze, follow, carry-as-kinematic, reset fallbacks
py -I tests\test_startstop.py   # Stop/Start, groups, restore mode, colliding paths
```

Stubbed PySide6 and VRED (translation-only matrices, so **rotation is not covered offline**;
it was verified in the headset). The stubs reproduce the real failures: colliding
`getPath()`, a `QMatrix4x4` without copy constructor, a body that only follows its node when
kinematic, and one that snaps back unless rebuilt. Add a stub for each new VRED behaviour.

## Open / next

- Not tried: VR controllers (no pinch signal; would need a trigger-based grab), two-handed
  grabs, throwing (release velocity), the "Kinematic (pushes others)" hold mode while held
  objects hit other parts, other OpenXR runtimes.
- Customer context lives in memory, not here (this skills repo is public).
