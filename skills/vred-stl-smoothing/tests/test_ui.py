import sys, types, importlib.util
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{}))
c = ns("PySide6.QtCore", Qt=base); gq = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=gq)),("PySide6.QtGui",gq),("PySide6.QtCore",c),("PySide6.QtWidgets",w)): sys.modules[n]=m
sys.modules["vrKernelServices"] = ns("vrKernelServices", vrdGeometryNode=lambda n: n, vrdSwitchNode=None, vrGeometryTypes=None,
    vrScenegraphTypes=types.SimpleNamespace(DuplicateOption=types.SimpleNamespace(DuplicateAll=0)), vrMaterialTypes=None, vrTextureTypes=types.SimpleNamespace(RepeatMode=types.SimpleNamespace(Repeat=1, Clamp=2)))
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.YIELD_EVERY = 500; m.SLICE_SECONDS = 0.0   # force many ticks

scene = []
class Geo:
    def __init__(s, name, pos, idx): s.name, s.pos, s.idx, s.vis, s.nrm = name, pos, idx, True, None
    getName = lambda s: s.name; setName = lambda s, n: setattr(s, 'name', n)
    getPositions = lambda s: s.pos; getIndices = lambda s: s.idx
    setPositions = lambda s, p: setattr(s, 'pos', p); setIndices = lambda s, i: setattr(s, 'idx', i)
    setNormals = lambda s, n: setattr(s, 'nrm', n); setVisibilityFlag = lambda s, v: setattr(s, 'vis', v)
    getParent = lambda s: types.SimpleNamespace(getChildren=lambda: list(scene))
def dup(nodes, opt):
    g = Geo(nodes[0].name, list(nodes[0].pos), list(nodes[0].idx)); scene.append(g); return [g]
m.vrScenegraphService = types.SimpleNamespace(duplicateNodes=dup)
m.vrGeometryService = types.SimpleNamespace(subdivideGeometryPhong=lambda n, i: None)
m.geometry_nodes = lambda roots: list(roots)

def grid(N):
    P = []
    for i in range(N):
        for j in range(N):
            a, b, c2, d = (i,j,0), (i+1,j,0), (i+1,j+1,0.1*i), (i,j+1,0)
            P += [*a, *b, *c2, *a, *c2, *d]
    return P
A = Geo("PartA", grid(40), list(range(40*40*6))); B = Geo("PartB", grid(30), list(range(30*30*6)))
scene += [A, B]

val = lambda x: types.SimpleNamespace(value=lambda: x, isChecked=lambda: x)
class Btn:
    def __init__(s): s.en = True
    def setEnabled(s, e): s.en = e
class Bar:
    def __init__(s): s.vals = []; s.fmt = ""
    def setValue(s, v): s.vals.append(v)
    def setFormat(s, f): s.fmt = f
class Timer:
    def __init__(s): s.on = False
    def start(s): s.on = True
    def stop(s): s.on = False
log = []
p = object.__new__(m.STLSmoothPanel)
p.__dict__.update(crease=val(40.0), tol=val(0.0), subdiv=val(0), keep=val(True), switch=val(False), label_scene=val(False),
    _say=log.append, _pending={}, _queue=[], _job=None, _settings=None, vrange=val(0.0),
    _buttons=[Btn(), Btn(), Btn()], cancel=Btn(), progress=Bar(), _timer=Timer())

p._smooth([A, B]); assert not p._buttons[0].en and p.cancel.en
p._smooth([A]); assert "Still processing" in log[-1]
ticks = 0
while p._timer.on: p._tick(); ticks += 1
print("ticks", ticks, "progress monotonic", p.progress.vals[:-1] == sorted(p.progress.vals[:-1]),
      "max", max(p.progress.vals), "buttons back", p._buttons[0].en, "fmt", p.progress.fmt)
print([ (g.name, g.vis, g.nrm is not None) for g in scene ])
print(log); assert A.nrm is None and B.nrm is None and not A.vis

# cancel mid-way: no new copy must appear
n_before = len(scene)
p.crease = val(20.0); p._smooth([A, B])
for _ in range(5): p._tick()
p._cancel()
print("after cancel: copies added", len(scene) - n_before, "| timer", p._timer.on, "| buttons", p._buttons[0].en)
assert len(scene) == n_before
print("\n".join(log))

# ---- defect run: always a copy, texcoords set, material applied, legend updated
class Lbl:
    def __init__(s): s.t = ""
    def setText(s, t): s.t = t
Geo.setTexCoords = lambda s, uv, slot, dim: setattr(s, 'uv', (uv, slot, dim))
applied = []
m.vrMaterialService = types.SimpleNamespace(applyMaterialToNodes=lambda mat, nodes: applied.append((mat, [g.name for g in nodes])))
p._texture_material = lambda name, *a: "MAT:" + name
p.__dict__.update(legend_lo=Lbl(), legend_mid=Lbl(), legend_hi=Lbl(), vrange=val(0.0), keep=val(True))
n0 = len(scene); log.clear()
p._smooth([A, B] + scene[2:], ("deviation", 20.0))
while p._timer.on: p._tick()
new = scene[n0:]
print("defect copies", [(g.name, g.vis, len(g.uv[0]) == 2*len(g.pos)//3, g.uv[1:]) for g in new])
print("applied", applied, "| legend", p.legend_lo.t, "|", p.legend_hi.t)
print("visible now", [g.name for g in scene if g.vis])
assert A.pos == A.pos and A.nrm is None and len(new) == 2 and all(g.vis for g in new)
p._smooth([A], ("curvature",))
while p._timer.on: p._tick()
print("curv:", scene[-1].name, "| legend", p.legend_lo.t, "|", p.legend_hi.t)
print("\n".join(log))

# ---- smoothed copy as source for defect map; name-collision safety
log.clear(); applied.clear()
A2 = Geo("PartA2", list(B.pos), list(B.idx)); scene.append(A2)       # similar name, other part
smooth_copy = [g for g in scene if g.name == "PartA_smooth_c40_s0"][0]
p._smooth([smooth_copy], ("deviation", 20.0))
while p._timer.on: p._tick()
print("new:", scene[-1].name, "| visible:", [g.name for g in scene if g.vis])
assert scene[-1].name == "PartA_defect_dev20" and A2.vis
assert [g.name for g in scene if g.vis and g.name.startswith("PartA_")] == ["PartA_defect_dev20"]
print(chr(10).join(log))
