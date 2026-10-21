"""Offline test of Stop / Start: physics groups, restore mode, home capture.

Run with `py -I test_startstop.py`. Grab, reset and carrying are in test_grab.py.
"""
import os
import sys
import types
import importlib.util

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugin", "PhysicsGrab", "vrPhysicsGrab.py")


def ns(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


base = type("Stub", (object,), {})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget", (base,), {}))
c = ns("PySide6.QtCore", QTimer=base)
g = ns("PySide6.QtGui", QVector3D=base)
for n, m in (("PySide6", ns("PySide6", QtCore=c, QtGui=g, QtWidgets=w)),
             ("PySide6.QtCore", c), ("PySide6.QtGui", g), ("PySide6.QtWidgets", w)):
    sys.modules[n] = m

CT = types.SimpleNamespace(Dynamic="Dyn", Static="Sta", Kinematic="Kin")


class Node:
    def __init__(self, name, children=(), active=True, kind="obj"):
        self.name, self.children, self.active, self.kind = name, list(children), active, kind
        self.mat, self.wake = "home", None
    def getChildren(self): return self.children
    def isType(self, t): return getattr(t, "kind", None) == self.kind
    def isInternal(self): return False
    def getName(self): return self.name
    def getPath(self): return "/PhysicsObject"      # as in VRED: paths collide
    def getObjectId(self): return id(self)
    def isValid(self): return True
    def isActive(self): return self.active
    def setActive(self, a): self.active = a
    def setWakeCounter(self, v): self.wake = v
    def getColliderType(self): return CT.Dynamic
    def getSceneNode(self): return self
    def getWorldTransform(self): return self.mat


class Kind:
    def __init__(self, kind): self.kind = kind
    def __call__(self, n): return n


sys.modules["vrKernelServices"] = ns(
    "vrKernelServices", vrdPhysicsObjectNode=Kind("obj"), vrdPhysicsGroupNode=Kind("grp"),
    vrdTransformNode=Kind("obj"), vrHandTypes=base,
    vrPhysicsTypes=types.SimpleNamespace(ColliderType=CT))
spec = importlib.util.spec_from_file_location("vrPhysicsGrab", PLUGIN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

a = Node("BoxA")
b = Node("BoxB", active=False)
grp = Node("Grp", [a, b], active=False, kind="grp")
root = Node("root", [grp], kind="grp")
mod.vrPhysicsService = types.SimpleNamespace(
    getRootNode=lambda: root, getDynamicObjects=lambda: [], getKinematicObjects=lambda: [],
    getPhysicsObject=lambda n: n)


def chk(v): return types.SimpleNamespace(isChecked=lambda: v)


logs = []
p = object.__new__(mod.PhysicsGrabPanel)
p.__dict__.update(_objects=[], _saved={}, _home={}, _groups=[], _stopped=False, _held=None,
                  _frozen=None, _types={}, _missed={}, _strategy=0, _carry=False,
                  chk_restore=chk(False), ed_filter=types.SimpleNamespace(text=lambda: ""),
                  ed_exclude=types.SimpleNamespace(text=lambda: "collider, collision_geo"),
                  status=types.SimpleNamespace(setText=lambda s: None))
p._log = logs.append

p.refresh()
assert [o.name for o in p._objects] == ["BoxA", "BoxB"]
assert [x.name for x in p._groups] == ["Grp"]
assert len(p._home) == 2, "colliding getPath() must not merge objects"

p.stop_physics()
assert not a.active and not b.active
a.mat = b.mat = "fallen"
p.refresh()                      # must not overwrite home
assert all(m == "home" for _, _, m in p._home.values())
p.start_physics()
assert a.active and b.active and grp.active, "Start must enable all objects and their groups"
assert a.wake == 0.4

# restore mode keeps previously-off objects off
b.active = False
p.chk_restore = chk(True)
p.stop_physics()
p.start_physics()
assert a.active and not b.active
print("OK")
print("\n".join(logs))
