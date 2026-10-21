"""PhysicsGrab - alpha: scene physics start/stop plus pinch-grab for VRED XR.

Start/Stop deactivates every physics object (vrdPhysicsObjectNode.setActive) one by
one and restores each object's previous state. The global simulation
(vrPhysicsService.setActive / setPaused) is never touched, so the built-in hand
interaction keeps running.

Pinch-grab (hand tracking): when the pinch strength passes the close threshold the
nearest filtered physics object inside the radius is attached to the pinch point and
follows the hand until the pinch drops below the release threshold.

Several behaviours are undocumented and must be confirmed in a headset; the panel
exposes them as settings and prints diagnostics to Scripts > Terminal.
"""
import time

from PySide6 import QtCore, QtGui, QtWidgets

try:
    from vrKernelServices import (vrdPhysicsObjectNode, vrdPhysicsGroupNode,
                                  vrdTransformNode, vrHandTypes, vrPhysicsTypes)
except ImportError:
    pass

_reported = set()


def _report(label, exc):
    """Print a failing VRED call once, so a silent failure is visible in the terminal."""
    key = (label, type(exc).__name__, str(exc))
    if key not in _reported:
        _reported.add(key)
        print("[PhysicsGrab] %s failed: %s: %s" % (label, type(exc).__name__, exc))


def _call(label, fn, *args):
    try:
        return fn(*args)
    except Exception as exc:
        _report(label, exc)
        return None


def _vec(m):
    c = m.column(3)
    return QtGui.QVector3D(c.x(), c.y(), c.z())


def _inverse(m):
    inv = m.inverted()
    return inv[0] if isinstance(inv, tuple) else inv   # PySide6 builds differ


def _or(value, fallback):
    # Explicit None test: Qt value types may define truthiness (a zero vector is falsy).
    return fallback if value is None else value


def _fmt(v):
    return "(%.0f, %.0f, %.0f)" % (v.x(), v.y(), v.z())


def _pos(m):
    c = m.column(3)
    return "(%.0f, %.0f, %.0f)" % (c.x(), c.y(), c.z())


def _dist(a, b):
    return ((a.x() - b.x()) ** 2 + (a.y() - b.y()) ** 2 + (a.z() - b.z()) ** 2) ** 0.5


def _key(obj):
    """Identity of a physics object. Not getPath(): every physics object is called
    "PhysicsObject", so their paths collide and the static floor ended up sharing a
    key (and so a collider type) with the dynamic parts."""
    node = obj.getSceneNode()
    if node is not None and node.isValid():
        return ("scene", node.getObjectId())
    return ("physics", obj.getObjectId())


def _label(obj):
    """The scene node's name: physics objects themselves are all "PhysicsObject"."""
    node = obj.getSceneNode()
    return node.getName() if node is not None and node.isValid() else obj.getName()


def _type_name(t):
    for n in ("Dynamic", "Kinematic", "Static"):
        if t == getattr(vrPhysicsTypes.ColliderType, n):
            return n
    return str(t)


def point_box_distance(p, bmin, bmax):
    """Distance from point p to an axis-aligned box (0 when inside)."""
    dx = max(bmin.x() - p.x(), 0.0, p.x() - bmax.x())
    dy = max(bmin.y() - p.y(), 0.0, p.y() - bmax.y())
    dz = max(bmin.z() - p.z(), 0.0, p.z() - bmax.z())
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def collect_physics_objects(group, name_filter="", out=None, groups=None, chain=()):
    """Walk the physics editor tree.

    Returns (objects, groups): every non-internal physics object matching the filter,
    and every group above one of them. An inactive group deactivates all its children
    regardless of their own state, so Start has to switch those groups on as well.
    """
    if out is None:
        out, groups = [], {}
    for child in group.getChildren():
        if child.isType(vrdPhysicsObjectNode):
            obj = vrdPhysicsObjectNode(child)
            if obj.isInternal():
                continue
            if name_filter and name_filter.lower() not in _label(obj).lower():
                continue
            out.append(obj)
            for g in chain:
                groups[g.getPath()] = g
        elif child.isType(vrdPhysicsGroupNode):
            g = vrdPhysicsGroupNode(child)
            collect_physics_objects(g, name_filter, out, groups, chain + (g,))
    return out, list(groups.values())


# Ways to move a physics object, tried in order until one sticks (see _place).
PLACE_STRATEGIES = ("reactivate", "rebuild", "kinematic drive")
PLACE_TOLERANCE = 20.0      # scene units; gravity alone moves a resting object less


class PhysicsGrabPanel(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._objects = []        # physics objects found by the last Refresh
        self._saved = {}          # path -> (object, was_active)
        self._home = {}           # path -> world transform at Refresh
        self._stopped = False
        self._groups = []         # physics groups above those objects
        self._types = {}          # path -> collider type at Refresh
        self._frozen = None       # dict(obj, hand, token): pinch closing on it
        self._missed = {}         # hand -> miss already logged for this pinch
        self._strategy = 0        # index into PLACE_STRATEGIES that last worked
        self._carry = False       # held objects need kinematic carrying (learned)
        self._held = None         # dict(obj, node, offset, hand, token)
        self._last_debug = 0.0

        self._build_ui()
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)

        if parent is not None:
            layout = parent.layout() or QtWidgets.QVBoxLayout(parent)
            layout.addWidget(self)
        self.refresh()

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        lay = QtWidgets.QVBoxLayout(self)

        self.status = QtWidgets.QLabel("")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        row = QtWidgets.QHBoxLayout()
        self.btn_stop = QtWidgets.QPushButton("Stop scene physics")
        self.btn_start = QtWidgets.QPushButton("Start scene physics")
        self.btn_stop.clicked.connect(self.stop_physics)
        self.btn_start.clicked.connect(self.start_physics)
        row.addWidget(self.btn_stop)
        row.addWidget(self.btn_start)
        lay.addLayout(row)

        self.chk_restore = QtWidgets.QCheckBox("Start restores state from before Stop")
        self.chk_restore.setToolTip("Off: Start switches every filtered object and its groups on.\n"
                                    "On: objects that were off before Stop stay off.")
        lay.addWidget(self.chk_restore)

        form = QtWidgets.QFormLayout()
        self.ed_filter = QtWidgets.QLineEdit()
        self.ed_filter.setPlaceholderText("name contains... (empty = all)")
        form.addRow("Object filter", self.ed_filter)
        self.ed_exclude = QtWidgets.QLineEdit("collider, collision_geo")
        self.ed_exclude.setToolTip("Comma-separated name parts to leave alone. The defaults are\n"
                                   "VRED's own hand colliders: grabbing or stopping those breaks\n"
                                   "the hand interaction.")
        form.addRow("Exclude names", self.ed_exclude)
        btn_refresh = QtWidgets.QPushButton("Refresh objects")
        btn_refresh.clicked.connect(self.refresh)
        form.addRow("", btn_refresh)
        lay.addLayout(form)

        grab = QtWidgets.QGroupBox("Pinch grab (hand tracking)")
        gf = QtWidgets.QFormLayout(grab)
        self.chk_grab = QtWidgets.QCheckBox("Enable pinch grab")
        self.chk_grab.toggled.connect(self._grab_toggled)
        gf.addRow(self.chk_grab)

        self.sp_radius = QtWidgets.QDoubleSpinBox()
        self.sp_radius.setRange(1.0, 100000.0)
        self.sp_radius.setValue(150.0)
        self.sp_radius.setSuffix(" scene units")
        self.sp_radius.setToolTip("Max distance from pinch point to an object's bounding box.")
        gf.addRow("Grab radius", self.sp_radius)

        self.sp_close = QtWidgets.QDoubleSpinBox()
        self.sp_close.setRange(0.0, 1.0)
        self.sp_close.setSingleStep(0.05)
        self.sp_close.setValue(0.80)
        gf.addRow("Pinch close", self.sp_close)

        self.sp_open = QtWidgets.QDoubleSpinBox()
        self.sp_open.setRange(0.0, 1.0)
        self.sp_open.setSingleStep(0.05)
        self.sp_open.setValue(0.50)
        gf.addRow("Pinch release", self.sp_open)

        self.cb_point = QtWidgets.QComboBox()
        self.cb_point.addItems(["Fingertips, joints relative to hand",
                                "Fingertips, joints in world space",
                                "Hand origin"])
        self.cb_point.setToolTip("Undocumented which space VRED returns joints in. If a pinch\n"
                                 "finds nothing, the log prints the pinch point and the nearest\n"
                                 "object's distance; try the other options.")
        gf.addRow("Pinch point", self.cb_point)

        self.sp_freeze = QtWidgets.QDoubleSpinBox()
        self.sp_freeze.setRange(0.0, 1.0)
        self.sp_freeze.setSingleStep(0.05)
        self.sp_freeze.setValue(0.30)
        self.sp_freeze.setToolTip("Once the pinch passes this value, the nearest object stops\n"
                                  "being simulated so closing fingers cannot push it away.")
        gf.addRow("Freeze target at", self.sp_freeze)

        self.cb_hold = QtWidgets.QComboBox()
        self.cb_hold.addItems(["Deactivate (no collisions)", "Kinematic (pushes others)"])
        self.cb_hold.setToolTip("How the target is taken out of the simulation while frozen\n"
                                "or held. Kinematic needs testing: VRED may need a rebuild.")
        gf.addRow("While held", self.cb_hold)

        self.hand_readout = QtWidgets.QLabel("hands: -")
        self.hand_readout.setWordWrap(True)
        gf.addRow(self.hand_readout)

        self.cb_follow = QtWidgets.QComboBox()
        self.cb_follow.addItems(["Pinch point + hand rotation",
                                 "Pinch point (position only)",
                                 "Hand origin (position + rotation)"])
        self.cb_follow.setToolTip("What the held object follows.")
        gf.addRow("Held object follows", self.cb_follow)

        self.chk_debug = QtWidgets.QCheckBox("Print hand debug (1 Hz, Terminal)")
        gf.addRow(self.chk_debug)
        lay.addWidget(grab)

        row = QtWidgets.QHBoxLayout()
        btn_home = QtWidgets.QPushButton("Capture home positions")
        btn_home.setToolTip("Store where every filtered object is now. Captured automatically\n"
                            "the first time an object is seen; press again to overwrite.")
        btn_home.clicked.connect(lambda: self.capture_home(overwrite=True))
        btn_reset = QtWidgets.QPushButton("Reset transforms")
        btn_reset.setToolTip("Put every filtered object back to its home position.")
        btn_reset.clicked.connect(self.reset_transforms)
        row.addWidget(btn_home)
        row.addWidget(btn_reset)
        lay.addLayout(row)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(200)
        self.log.setMinimumHeight(90)
        lay.addWidget(self.log)
        lay.addStretch(1)

    def _log(self, msg):
        print("[PhysicsGrab] " + msg)
        self.log.appendPlainText(msg)

    def _update_status(self):
        n = len(self._objects)
        active = sum(1 for o in self._objects if _call("isActive", o.isActive))
        state = "STOPPED" if self._stopped else "running"
        held = self._held["node"].getName() if self._held else "-"
        self.status.setText("%d physics objects (%d active) | scene physics: %s | held: %s"
                            % (n, active, state, held))

    # ------------------------------------------------------ start / stop
    def refresh(self):
        if self._held:
            self._release()
        self._unfreeze()
        root = _call("getRootNode", vrPhysicsService.getRootNode)
        if root:
            self._objects, self._groups = collect_physics_objects(root, self.ed_filter.text().strip())
        else:
            self._objects, self._groups = [], []
        self._types = {_key(o): _call("getColliderType", o.getColliderType)
                       for o in self._objects}
        self._add_service_objects()
        excl = [x.strip().lower() for x in self.ed_exclude.text().split(",") if x.strip()]
        if excl:
            dropped = [o for o in self._objects if any(x in _label(o).lower() for x in excl)]
            if dropped:
                ids = {id(o) for o in dropped}
                self._objects = [o for o in self._objects if id(o) not in ids]
                self._log("excluded %d (hand colliders etc.): %s" % (
                    len(dropped), ", ".join(sorted({_label(o) for o in dropped}))))
        self.capture_home(overwrite=False)
        self._log("objects: " + ", ".join("%s [%s%s]" % (
            _label(o), _type_name(self._types[_key(o)]),
            "" if self._is_candidate(o) else ", not grabbable") for o in self._objects[:12]))
        self._update_status()

    def _add_service_objects(self):
        """Merge in what the physics service itself reports as dynamic / kinematic.

        The editor tree can miss objects: the walk skips internal (system-created)
        objects, and VR can register scene parts that way. The service lists are the
        authority on collider type too, so they override getColliderType. Internal
        (system-created) objects are left out: VRED's hand colliders are internal,
        dynamic and kinematic alike.
        """
        known = {_key(o): o for o in self._objects}
        name_filter = self.ed_filter.text().strip().lower()
        counts = {}
        for label, getter, ctype, allow_internal in (
                ("dynamic", vrPhysicsService.getDynamicObjects,
                 vrPhysicsTypes.ColliderType.Dynamic, False),
                ("kinematic", vrPhysicsService.getKinematicObjects,
                 vrPhysicsTypes.ColliderType.Kinematic, False)):
            nodes = _call(label + " objects", getter) or []
            counts[label] = len(nodes)
            for node in nodes:
                obj = _call("getPhysicsObject", vrPhysicsService.getPhysicsObject, node)
                if obj is None or not obj.isValid():
                    continue
                if obj.isInternal() and not allow_internal:
                    continue
                if name_filter and name_filter not in node.getName().lower():
                    continue
                key = _key(obj)
                if key not in known:
                    known[key] = obj
                    self._objects.append(obj)
                self._types[key] = ctype
        self._log("physics service reports %d dynamic, %d kinematic; %d objects in total"
                  % (counts.get("dynamic", 0), counts.get("kinematic", 0), len(known)))

    def capture_home(self, overwrite):
        """Remember each object's world transform. Without overwrite, only objects not
        seen before are stored, so a Refresh after things have fallen keeps the
        original positions."""
        n = 0
        for o in self._objects:
            key = _key(o)
            if key in self._home and not overwrite:
                continue
            node = o.getSceneNode()
            if node and node.isValid():
                self._home[key] = (o, node, node.getWorldTransform())
                n += 1
        if overwrite:
            self._log("captured home positions of %d objects" % n)

    def stop_physics(self):
        if self._held:
            self._release()
        self.refresh()
        if not self._stopped:
            self._saved = {_key(o): (o, bool(o.isActive())) for o in self._objects}
        for o in self._objects:
            _call("setActive(False)", o.setActive, False)
        self._stopped = True
        self._log("stopped %d objects (global simulation left running)" % len(self._objects))
        self._update_status()

    def _activate(self, obj, active):
        _call("setActive", obj.setActive, active)
        if active:
            # Woken explicitly: a re-activated object can otherwise stay asleep until
            # something touches it, which looks like "only some objects started".
            _call("setWakeCounter", obj.setWakeCounter, 0.4)

    def start_physics(self):
        if self._held:
            self._release()
        self.refresh()
        groups_on = 0
        for g in self._groups:
            if g.isValid() and not g.isActive():
                _call("group.setActive", g.setActive, True)
                groups_on += 1
        restore = self.chk_restore.isChecked() and self._saved
        n = 0
        for o in self._objects:
            want = True
            if restore and _key(o) in self._saved:
                want = self._saved[_key(o)][1]
            self._activate(o, want)
            n += int(want)
        still_off = [_label(o) for o in self._objects if not _call("isActive", o.isActive)]
        self._log("started %d objects, switched on %d groups%s" % (
            n, groups_on, " (restored previous state)" if restore else ""))
        if still_off and not restore:
            self._log("still inactive after Start: " + ", ".join(still_off[:10]))
        self._saved = {}
        self._stopped = False
        self._update_status()

    # ------------------------------------------------------ placing objects
    def _suspend(self, obj):
        """Take obj out of the simulation; return what _resume needs to undo it."""
        token = {"active": bool(_call("isActive", obj.isActive)), "type": None}
        if self.cb_hold.currentIndex() == 1 and token["active"]:
            token["type"] = _call("getColliderType", obj.getColliderType)
            _call("setColliderType(Kinematic)", obj.setColliderType,
                  vrPhysicsTypes.ColliderType.Kinematic)
        else:
            _call("setActive(False)", obj.setActive, False)
        return token

    def _resume(self, obj, token):
        if not obj.isValid():
            return
        if token["type"] is not None:
            _call("setColliderType(restore)", obj.setColliderType, token["type"])
        if token["active"]:
            self._activate(obj, True)
        elif token.get("forced_on"):
            # Switched on as kinematic only to be carried; it was off before (Stop).
            _call("setActive(False)", obj.setActive, False)

    def _carry_kinematic(self, obj, token):
        """Switch a held object to kinematic and on, so its body follows the node.

        A deactivated body can still own its node's pose: the node then ignores every
        setWorldTransform (seen in VRED: 45 updates, target moved 54, object moved 0).
        A kinematic body is driven by its node instead, and nothing can push it.
        """
        if token["type"] is None:
            token["type"] = _or(self._types.get(_key(obj)),
                                _call("getColliderType", obj.getColliderType))
        token["forced_on"] = not token["active"]
        _call("setColliderType(Kinematic)", obj.setColliderType,
              vrPhysicsTypes.ColliderType.Kinematic)
        _call("setActive(True)", obj.setActive, True)

    def reset_transforms(self):
        if self._held:
            self._release()
        self._unfreeze()
        n, skipped = 0, []
        for obj, node, mat in self._home.values():
            if not node.isValid() or not obj.isValid():
                continue
            if self._types.get(_key(obj)) in (None, vrPhysicsTypes.ColliderType.Static):
                continue        # static floors never move; toggling them drops objects
            if not node.isType(vrdTransformNode):
                # Plain group nodes have no transform of their own and cannot be moved.
                skipped.append(node.getName())
                continue
            token = self._suspend(obj)
            self._place(obj, vrdTransformNode(node), mat, token, self._strategy)
            n += 1
        self._log("resetting %d objects (method: %s)" % (n, PLACE_STRATEGIES[self._strategy]))
        if skipped:
            self._log("not movable (scene node is not a transform node): " + ", ".join(skipped[:10]))

    def _place(self, obj, tnode, mat, token, strategy, verify=True):
        """Move a suspended physics object to mat and hand it back to the simulation.

        Moving the scene node alone is not enough if VRED keeps the body's own pose and
        writes it back over the node when the object is switched on again. Each
        strategy tries a different way round that; _check_place verifies the result and
        moves on to the next strategy if the object snapped back.
        """
        _call("setWorldTransform", tnode.setWorldTransform, mat)
        name = PLACE_STRATEGIES[strategy]
        if name == "kinematic drive" and token["active"]:
            # A kinematic body follows its node, so drive it there, then go dynamic.
            old = token["type"] if token["type"] is not None else \
                _call("getColliderType", obj.getColliderType)
            _call("setColliderType(Kinematic)", obj.setColliderType,
                  vrPhysicsTypes.ColliderType.Kinematic)
            _call("setActive(True)", obj.setActive, True)

            def finish():
                _call("setWorldTransform", tnode.setWorldTransform, mat)
                _call("setColliderType(restore)", obj.setColliderType, old)
                self._activate(obj, True)
            QtCore.QTimer.singleShot(200, finish)
            delay = 250
        else:
            if name == "rebuild":
                _call("rebuild", obj.rebuild)
            # One physics step with the body out of the simulation, then set the pose
            # again just before it comes back.
            def finish():
                _call("setWorldTransform", tnode.setWorldTransform, mat)
                self._resume(obj, token)
            QtCore.QTimer.singleShot(100, finish)
            delay = 150
        if verify and token["active"]:
            # A released object falls, so only placements (Reset) are verified.
            QtCore.QTimer.singleShot(delay + 150, lambda: self._check_place(obj, tnode, mat, strategy))

    def _check_place(self, obj, tnode, mat, strategy):
        if not tnode.isValid():
            return
        off = _dist(_vec(tnode.getWorldTransform()), _vec(mat))
        name = PLACE_STRATEGIES[strategy]
        if off <= PLACE_TOLERANCE:
            if self._strategy != strategy:
                self._strategy = strategy
            self._log("%s placed OK with '%s'" % (tnode.getName(), name))
            return
        self._log("%s ended %.0f away from target with '%s' (now %s, target %s)"
                  % (tnode.getName(), off, name, _pos(tnode.getWorldTransform()), _pos(mat)))
        if strategy + 1 < len(PLACE_STRATEGIES):
            self._log("  trying '%s'" % PLACE_STRATEGIES[strategy + 1])
            token = self._suspend(obj)
            self._place(obj, tnode, mat, token, strategy + 1)
        else:
            self._log("  all methods failed: physics owns this pose; send this log")

    # ---------------------------------------------------------- pinch grab
    def _grab_toggled(self, on):
        if on:
            self.refresh()
            self._timer.start()
            self._log("pinch grab on")
        else:
            self._timer.stop()
            if self._held:
                self._release()
            self._unfreeze()
            self.hand_readout.setText("hands: -")
            self._log("pinch grab off")

    def _pinch_point(self, hand):
        """World position between thumb tip and index tip, or None."""
        try:
            t = hand.getJointTransform(vrHandTypes.FingerType.Thumb, 4)
            i = hand.getJointTransform(vrHandTypes.FingerType.Index, 4)
        except Exception as exc:
            _report("getJointTransform", exc)
            return None
        mode = self.cb_point.currentIndex()
        if mode == 2:
            return _vec(hand.getTransform())
        if mode == 0:
            m = hand.getTransform()
            t = m * t
            i = m * i
        tp = t.column(3)
        ip = i.column(3)
        return QtGui.QVector3D((tp.x() + ip.x()) / 2, (tp.y() + ip.y()) / 2, (tp.z() + ip.z()) / 2)

    def _hands(self):
        """Tracked hands as (name, hand), and a one-line readout of the raw values."""
        out, parts = [], []
        for name, getter in (("right", vrDeviceService.getRightTrackedHand),
                             ("left", vrDeviceService.getLeftTrackedHand)):
            h = _call("get%sTrackedHand" % name, getter)
            if h is None:
                parts.append("%s n/a" % name)
            elif not _call("isTracked", h.isTracked):
                parts.append("%s not tracked" % name)
            else:
                parts.append("%s pinch %.2f" % (name, h.getPinchStrength()))
                out.append((name, h))
        state = "-"
        if self._held:
            state = "holding " + self._held["node"].getName()
        elif self._frozen:
            state = "frozen " + _label(self._frozen["obj"])
        self.hand_readout.setText(" | ".join(parts) + " | " + state)
        return out

    def _is_candidate(self, o):
        # Static floors and shadow planes have huge bounding boxes that would otherwise
        # always win. Kinematic stays grabbable: an earlier build could leave objects
        # switched to Kinematic, and a kinematic part is meant to be moved anyway.
        if self._types.get(_key(o)) in (None, vrPhysicsTypes.ColliderType.Static):
            return False
        node = o.getSceneNode()
        return bool(node) and node.isValid() and node.isType(vrdTransformNode)

    def _nearest(self, point):
        best, best_key = None, None
        radius = self.sp_radius.value()
        for o in self._objects:
            if not o.isValid() or not self._is_candidate(o):
                continue
            bb = o.getSceneNode().getWorldBoundingBox()
            d = point_box_distance(point, bb.getMin(), bb.getMax())
            if d > radius:
                continue
            key = (d, (bb.getCenter() - point).length())   # inside two boxes: closer centre wins
            if best_key is None or key < best_key:
                best, best_key = o, key
        return best

    def _tick(self):
        try:
            hands = self._hands()
            now = time.time()
            if self.chk_debug.isChecked() and now - self._last_debug > 1.0:
                self._last_debug = now
                for name, h in hands:
                    p = self._pinch_point(h)
                    print("[PhysicsGrab] %s pinch=%.2f point=%s" % (
                        name, h.getPinchStrength(),
                        None if p is None else "(%.1f, %.1f, %.1f)" % (p.x(), p.y(), p.z())))

            by_name = dict(hands)
            if self._held:
                hand = by_name.get(self._held["hand"])
                if hand is None or hand.getPinchStrength() < self.sp_open.value():
                    self._release()
                else:
                    self._follow(hand)
                return

            if self._frozen:
                hand = by_name.get(self._frozen["hand"])
                s = hand.getPinchStrength() if hand is not None else 0.0
                if s >= self.sp_close.value():
                    self._grab(hand)
                elif s < self.sp_freeze.value() - 0.05:
                    self._unfreeze()
                return

            for name, h in hands:
                s = h.getPinchStrength()
                if s < self.sp_open.value():
                    self._missed[name] = False      # log a miss once per pinch
                if s < min(self.sp_freeze.value(), self.sp_close.value()):
                    continue
                p = self._pinch_point(h)
                obj = self._nearest(p) if p is not None else None
                if obj is None:
                    if s >= self.sp_close.value() and not self._missed.get(name):
                        self._missed[name] = True
                        self._log_miss(name, h, p)
                    continue
                self._freeze(obj, name)
                if s >= self.sp_close.value():
                    self._grab(h)
                return
        except Exception as exc:
            # Shown in the panel too: a failing tick otherwise looks like "nothing happens".
            msg = "tick failed: %s: %s" % (type(exc).__name__, exc)
            if msg != getattr(self, "_last_tick_error", None):
                self._last_tick_error = msg
                self._log(msg)

    def _log_miss(self, name, hand, p):
        if p is None:
            self._log("%s pinch: no pinch point (see Terminal)" % name)
            return
        best = None
        for o in self._objects:
            if o.isValid() and self._is_candidate(o):
                bb = o.getSceneNode().getWorldBoundingBox()
                d = point_box_distance(p, bb.getMin(), bb.getMax())
                if best is None or d < best[0]:
                    best = (d, _label(o))
        self._log("%s pinch found nothing: point (%.0f, %.0f, %.0f), hand %s, nearest %s"
                  % (name, p.x(), p.y(), p.z(), _pos(hand.getTransform()),
                     "none grabbable" if best is None else
                     "%s at %.0f (radius %.0f)" % (best[1], best[0], self.sp_radius.value())))

    def _freeze(self, obj, hand_name):
        self._frozen = {"obj": obj, "hand": hand_name, "token": self._suspend(obj)}

    def _unfreeze(self):
        f, self._frozen = self._frozen, None
        if f is not None:
            self._resume(f["obj"], f["token"])

    def _grip_frame(self, hand):
        """The hand's rotation, placed at the pinch point.

        Following this frame makes a held object turn with the wrist around the point
        between the fingertips, not around the hand origin, so it does not swing away.
        Built as translate * hand rather than by editing a copy (no copy constructor).
        """
        hand_m = hand.getTransform()
        pinch = _or(self._pinch_point(hand), _vec(hand_m))
        move = QtGui.QMatrix4x4()
        move.translate(pinch - _vec(hand_m))
        return move * hand_m

    def _grab(self, hand):
        f, self._frozen = self._frozen, None
        obj = f["obj"]
        node = obj.getSceneNode()
        start = node.getWorldTransform()
        hand_m = hand.getTransform()
        inv = hand_m.inverted()
        if isinstance(inv, tuple):      # PySide6 builds differ: matrix or (matrix, ok)
            inv = inv[0]
        pinch = self._pinch_point(hand)
        if pinch is None:
            pinch = _vec(hand_m)
        self._held = {"obj": obj, "node": node, "hand": f["hand"], "token": f["token"],
                      "offset": inv * start,                  # node relative to hand
                      "grip_offset": _inverse(self._grip_frame(hand)) * start,
                      "start": start,
                      "grip": _vec(start) - pinch,            # node relative to pinch point
                      "hand0": _vec(hand_m), "pinch0": pinch, "target": start, "ticks": 0}
        if self._carry:
            self._held["carried"] = True
            self._carry_kinematic(obj, f["token"])
        self._log("grabbed %s with %s hand: object %s, pinch %s, hand %s" % (
            _label(obj), f["hand"], _pos(start), _fmt(pinch), _pos(hand_m)))
        self._update_status()

    def _follow(self, hand):
        h = self._held
        node = h["node"]
        if not node.isValid():
            self._held = None
            return
        if h["ticks"] >= 5 and not h.get("carried") and \
                _dist(_vec(node.getWorldTransform()), _vec(h["target"])) > PLACE_TOLERANCE:
            h["carried"] = self._carry = True
            self._carry_kinematic(h["obj"], h["token"])
            self._log("%s ignores moves while deactivated; carrying it as kinematic"
                      % _label(h["obj"]))
        mode = self.cb_follow.currentIndex()
        if mode == 0:
            target = self._grip_frame(hand) * h["grip_offset"]
        elif mode == 2:
            target = hand.getTransform() * h["offset"]
        else:
            # Position only, from the pinch point: keeps the object's own rotation.
            pinch = self._pinch_point(hand)
            if pinch is None:
                pinch = _vec(hand.getTransform())
            t = pinch + h["grip"]
            # Translate the start pose by the pinch offset. Not QMatrix4x4(start): VRED's
            # PySide6 has no copy constructor, and that TypeError stopped every update.
            move = QtGui.QMatrix4x4()
            move.translate(t - _vec(h["start"]))
            target = move * h["start"]
        vrdTransformNode(node).setWorldTransform(target)
        h["target"] = target
        h["ticks"] += 1

    def _release(self):
        h, self._held = self._held, None
        if h is None:
            return
        node = h["node"]
        if node.isValid():
            mat = node.getWorldTransform()
            hand = dict(self._hands()).get(h["hand"])
            # Which link broke if the object did not move: the hand pose, the pinch
            # point, our target, or the node ignoring the target.
            self._log("hold %s: %d updates; hand moved %s, pinch moved %s, target moved %.0f, "
                      "object moved %.0f, object vs target %.0f" % (
                          _label(h["obj"]), h["ticks"],
                          "n/a" if hand is None else "%.0f" % _dist(_vec(hand.getTransform()), h["hand0"]),
                          "n/a" if hand is None else "%.0f" % _dist(_or(self._pinch_point(hand), h["pinch0"]), h["pinch0"]),
                          _dist(_vec(h["target"]), _vec(h["start"])),
                          _dist(_vec(mat), _vec(h["start"])),
                          _dist(_vec(mat), _vec(h["target"]))))
            self._place(h["obj"], vrdTransformNode(node), mat, h["token"], self._strategy, verify=False)
            self._log("released %s at %s" % (node.getName(), _pos(mat)))
        else:
            self._resume(h["obj"], h["token"])
        self._update_status()


try:
    _host = VREDPluginWidget
except NameError:
    _host = None

if _host is not None:
    physicsGrabPanel = PhysicsGrabPanel(_host)
