import sys, types, importlib.util

import os
PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugin", "PhysicsGrab", "vrPhysicsGrab.py")


def ns(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


class V:
    def __init__(self, x=0, y=0, z=0): self._v = (x, y, z)
    def x(self): return self._v[0]
    def y(self): return self._v[1]
    def z(self): return self._v[2]
    def __sub__(self, o): return V(*(a - b for a, b in zip(self._v, o._v)))
    def __add__(self, o): return V(*(a + b for a, b in zip(self._v, o._v)))
    def length(self): return sum(a * a for a in self._v) ** 0.5


class M:  # translation-only matrix
    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, M): raise TypeError("no copy constructor (as in VRED PySide6)")
        self.t = V(x, y, z)
    def setColumn(self, i, v): self.t = V(v[0], v[1], v[2])
    def translate(self, v): self.t = self.t + v
    def __mul__(self, o): return M(*(a + b for a, b in zip(self.t._v, o.t._v)))
    def inverted(self): return (M(*(-a for a in self.t._v)), True)
    def column(self, i): return self.t


class Timer:
    @staticmethod
    def singleShot(ms, fn): fn()


base = type("Stub", (object,), {})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget", (base,), {}))
c = ns("PySide6.QtCore", QTimer=Timer)
g = ns("PySide6.QtGui", QVector3D=V, QMatrix4x4=M, QVector4D=lambda *a: a)
for n, m in (("PySide6", ns("PySide6", QtCore=c, QtGui=g, QtWidgets=w)),
             ("PySide6.QtCore", c), ("PySide6.QtGui", g), ("PySide6.QtWidgets", w)):
    sys.modules[n] = m

CT = types.SimpleNamespace(Dynamic="Dyn", Static="Sta", Kinematic="Kin")


class BB:
    def __init__(self, lo, hi): self.lo, self.hi = V(*lo), V(*hi)
    def getMin(self): return self.lo
    def getMax(self): return self.hi
    def getCenter(self): return V(*((a + b) / 2 for a, b in zip(self.lo._v, self.hi._v)))


class Obj:
    kind = "obj"
    def __init__(self, name, ctype, lo, hi):
        self.name, self.ctype, self.active, self.wake = name, ctype, True, None
        self.size = [h - l for l, h in zip(lo, hi)]
        self.mat = M(*((l + h) / 2 for l, h in zip(lo, hi)))
        self.home = self.mat
    def isType(self, t): return t in (OBJ, TN)
    def getChildren(self): return []
    def isInternal(self): return False
    def getName(self): return self.name
    def getPath(self): return "/PhysicsObject"   # real VRED: all physics objects share this
    def getObjectId(self): return id(self)
    def isValid(self): return True
    def isActive(self): return self.active
    def setActive(self, a): self.active = a
    def setWakeCounter(self, v): self.wake = v
    def getColliderType(self): return self.ctype
    def rebuild(self): pass
    def setColliderType(self, t): self.ctype = t
    def getSceneNode(self): return self
    def getWorldTransform(self): return self.mat
    def setWorldTransform(self, m): self.mat = m
    def getWorldBoundingBox(self):
        c = self.mat.t._v
        return BB([a - s / 2 for a, s in zip(c, self.size)], [a + s / 2 for a, s in zip(c, self.size)])


class Root:
    def __init__(self, kids): self.kids = kids
    def getChildren(self): return self.kids


OBJ, GRP, TN = object(), object(), (lambda n: n)
sys.modules["vrKernelServices"] = ns(
    "vrKernelServices", vrdPhysicsObjectNode=lambda n: n, vrdPhysicsGroupNode=lambda n: n,
    vrdTransformNode=TN, vrHandTypes=types.SimpleNamespace(FingerType=types.SimpleNamespace(Thumb=0, Index=1)),
    vrPhysicsTypes=types.SimpleNamespace(ColliderType=CT))
spec = importlib.util.spec_from_file_location("vrPhysicsGrab", PLUGIN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.vrdPhysicsObjectNode, mod.vrdPhysicsGroupNode, mod.vrdTransformNode = OBJ, GRP, TN
# isType checks identity against these markers; casts just return the node
mod.vrdPhysicsObjectNode = type("C", (), {"__new__": lambda cls, n: n})
OBJ_CLS = mod.vrdPhysicsObjectNode
Obj.isType = lambda self, t: t is OBJ_CLS or t is TN

plane = Obj("ShadowPlane", CT.Static, (-5000, -5000, -1), (5000, 5000, 1))
box = Obj("Box", CT.Dynamic, (0, 0, 0), (100, 100, 100))
sphere = Obj("Sphere", CT.Dynamic, (300, 0, 0), (400, 100, 100))
def svc(tree, dyn=()): return types.SimpleNamespace(getRootNode=lambda: Root(tree), getDynamicObjects=lambda: list(dyn), getKinematicObjects=lambda: [], getPhysicsObject=lambda n: n)
mod.vrPhysicsService = svc([plane, box, sphere])


class Hand:
    def __init__(self): self.pos, self.pinch = M(50, 50, 50), 0.0
    def isTracked(self): return True
    def getPinchStrength(self): return self.pinch
    def getTransform(self): return self.pos
    def getJointTransform(self, f, j): return M(0, 0, 0)


right = Hand()
mod.vrDeviceService = types.SimpleNamespace(getRightTrackedHand=lambda: right,
                                            getLeftTrackedHand=lambda: None)


def val(v): return types.SimpleNamespace(value=lambda: v)
def chk(v): return types.SimpleNamespace(isChecked=lambda: v)


logs = []
p = object.__new__(mod.PhysicsGrabPanel)
p.__dict__.update(_objects=[], _saved={}, _home={}, _groups=[], _stopped=False, _held=None,
                  _frozen=None, _types={}, _last_debug=0.0,
                  chk_restore=chk(False), cb_point=types.SimpleNamespace(currentIndex=lambda: 0), _missed={}, _strategy=0, chk_debug=chk(False),
                  ed_filter=types.SimpleNamespace(text=lambda: ""),
                  status=types.SimpleNamespace(setText=lambda s: None),
                  hand_readout=types.SimpleNamespace(setText=lambda s: None),
                  sp_radius=val(150.0), sp_close=val(0.8), sp_open=val(0.5), sp_freeze=val(0.3),
                  cb_hold=types.SimpleNamespace(currentIndex=lambda: 0), cb_follow=types.SimpleNamespace(currentIndex=lambda: 0), ed_exclude=types.SimpleNamespace(text=lambda: "collider, collision_geo"))
p._log = logs.append
p.refresh()

# pinch inside box and plane bounding boxes: must pick box, never the static plane
right.pinch = 0.4; p._tick()
assert p._frozen and p._frozen["obj"] is box, p._frozen
assert not box.active, "frozen target is out of the simulation (finger cannot push it)"
right.pinch = 0.9; p._tick()
assert p._held and p._held["obj"] is box
right.pos = M(1050, 50, 50); p._tick()
assert box.mat.t.x() == 1050, (box.mat.t.x(), logs)
assert p._held["ticks"] == 1
right.pinch = 0.1; p._tick()
assert p._held is None and box.active and box.wake == 0.4

# freeze then open without grabbing restores the object
right.pos = M(350, 50, 50); right.pinch = 0.4; p._tick()
assert p._frozen["obj"] is sphere and not sphere.active
right.pinch = 0.1; p._tick()
assert p._frozen is None and sphere.active

# nothing dynamic in range: plane is never picked
right.pos = M(-3000, -3000, 0); right.pinch = 0.9; p._tick()
assert p._held is None and p._frozen is None and plane.active

# reset puts the box home and reactivates it
p.reset_transforms()
assert box.mat.t.x() == 50 and box.active, box.mat.t.x()

# kinematic mode
p.cb_hold = types.SimpleNamespace(currentIndex=lambda: 1)
right.pos = M(50, 50, 50); right.pinch = 0.9; p._tick()
assert p._held and box.ctype == CT.Kinematic and box.active
right.pinch = 0.0; p._tick()
assert box.ctype == CT.Dynamic
# snap-back body: reactivating restores the body pose unless rebuilt first
class SnapObj(Obj):
    def setActive(self, a):
        if a and not self.active and not getattr(self, "rebuilt", False):
            self.mat = self.body
        self.active = a
    def rebuild(self): self.rebuilt = True
snap = SnapObj("Snap", CT.Dynamic, (1000, 0, 0), (1100, 100, 100))
mod.vrPhysicsService = svc([plane, snap])
p.cb_hold = types.SimpleNamespace(currentIndex=lambda: 0)
p._home = {}; p.refresh()
snap.mat = snap.body = M(2000, 0, 0)
p.reset_transforms()
assert snap.mat.t.x() == 1050 and snap.active, snap.mat.t.x()
assert p._strategy == 1, p._strategy
# internal dynamic object only reported by the service, with getColliderType failing
hidden = Obj("HiddenBox", CT.Dynamic, (0, 0, 0), (100, 100, 100))
hidden.isInternal = lambda: True
def boom(): raise RuntimeError("nope")
hidden.getColliderType = boom
mod.vrPhysicsService = svc([plane, hidden], dyn=[hidden])
p._home = {}; p.refresh()
assert hidden not in p._objects, "internal (hand) objects must be left alone"
coll = Obj("R_index_collision_geo", CT.Dynamic, (0, 0, 0), (10, 10, 10))
mod.vrPhysicsService = svc([plane, coll, box])
p._home = {}; p.refresh()
assert coll not in p._objects and box in p._objects
# body owns the pose while deactivated: only a kinematic, active body follows the node
class Sticky(Obj):
    def setWorldTransform(self, m):
        if self.active and self.ctype == CT.Kinematic:
            self.mat = m
sticky = Sticky("Sticky", CT.Dynamic, (0, 0, 0), (100, 100, 100))
mod.vrPhysicsService = svc([plane, sticky])
p.cb_hold = types.SimpleNamespace(currentIndex=lambda: 0)
p._home = {}; p._held = None; p._frozen = None; p.refresh()
right.pos = M(50, 50, 50); right.pinch = 0.9; p._tick()
assert p._held and p._held["obj"] is sticky
for i in range(8):
    right.pos = M(50 + 10 * (i + 1), 50, 50); p._tick()
assert p._held.get("carried") and sticky.ctype == CT.Kinematic and sticky.active
assert sticky.mat.t.x() == 130, sticky.mat.t.x()
right.pinch = 0.0; p._tick()
assert sticky.ctype == CT.Dynamic and sticky.active, (sticky.ctype, sticky.active, p._held, p._strategy, logs[-4:])
# next grab carries straight away
right.pinch = 0.9; p._tick(); right.pos = M(300, 50, 50); p._tick()
assert sticky.mat.t.x() == 300 - 130 + 130 or sticky.mat.t.x() > 130, sticky.mat.t.x()
print("OK"); print("\n".join(logs[-8:]))








