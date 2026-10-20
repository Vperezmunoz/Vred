import sys, types, importlib.util
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{})); c = ns("PySide6.QtCore", Qt=base); g = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=g)),("PySide6.QtCore",c),("PySide6.QtWidgets",w),("PySide6.QtGui",g)): sys.modules[n]=m
SWITCH = object()
class Kids(list):
    def __init__(s, owner): super().__init__(); s.owner = owner
    def append(s, node):
        if node.parent is not None: list.remove(node.parent.children, node)
        node.parent = s.owner; list.append(s, node)
_id = [0]
class Node:
    def __init__(s, name, kind="geo", pos=None, idx=None):
        _id[0] += 1; s.oid = _id[0]; s.name = name; s.kind = kind; s.parent = None
        s.children = Kids(s); s.vis = True; s.pos = pos; s.idx = idx; s.nrm = None; s.choice = -1; s.uv = None
    def getObjectId(s): return s.oid
    def getName(s): return s.name
    def setName(s, n): s.name = n
    def getParent(s): return s.parent
    def getChildren(s): return list(s.children)
    def isType(s, t): return (t is SWITCH) == (s.kind == "switch")
    def setVisibilityFlag(s, v): s.vis = v
    def getPositions(s): return s.pos
    def getIndices(s): return s.idx
    def setPositions(s, p): s.pos = p
    def setIndices(s, i): s.idx = i
    def setNormals(s, n): s.nrm = n
    def setTexCoords(s, uv, a, b): s.uv = uv
    def setChoice(s, k): s.choice = k
    def getWorldBoundingBox(s): return types.SimpleNamespace(getMax=lambda: (1, 2, 3))
sys.modules["vrKernelServices"] = ns("vrKernelServices", vrdGeometryNode=lambda n: n, vrdSwitchNode=SWITCH, vrGeometryTypes=None,
    vrScenegraphTypes=types.SimpleNamespace(DuplicateOption=types.SimpleNamespace(DuplicateAll=0), NodeType=types.SimpleNamespace(SwitchNode="sw")),
    vrMaterialTypes=None, vrTextureTypes=types.SimpleNamespace(RepeatMode=types.SimpleNamespace(Clamp=2)))
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.vrdSwitchNode = SWITCH
_cast = lambda n: n
m.vrdSwitchNode = SWITCH
# vrdSwitchNode(x) is used as a cast in the plugin; make SWITCH callable-compatible
class SwitchType:
    def __call__(s, n): return n
SW = SwitchType(); m.vrdSwitchNode = SW
Node.isType = lambda s, t: (t is SW) == (s.kind == "switch") if t is SW else False
def create(kind, parent, name):
    n = Node(name, "switch"); parent.children.append(n); return n
def dup(nodes, opt):
    src = nodes[0]; d = Node(src.name, pos=list(src.pos), idx=list(src.idx)); src.parent.children.append(d); return [d]
m.vrScenegraphService = types.SimpleNamespace(createNode=create, duplicateNodes=dup)
m.vrGeometryService = types.SimpleNamespace(subdivideGeometryPhong=lambda n, i: None)
m.vrMaterialService = types.SimpleNamespace(applyMaterialToNodes=lambda mat, nodes: None)
notes = []
class Ann:
    def __init__(s, name): s.name = name; notes.append(s)
    def setText(s, t): s.text = t
    def setSceneNode(s, n): s.node = n
    def setUseSceneNodeVisibility(s, v): s.usevis = v
    def setPosition(s, p): s.pos = p
m.vrAnnotationService = types.SimpleNamespace(createAnnotation=Ann)
m.geometry_nodes = lambda roots: list(roots)

def grid(N):
    P = []
    for i in range(N):
        for j in range(N):
            q = [(i,j,0), (i+1,j,0), (i+1,j+1,0.05*((i+j)%3)), (i,j+1,0)]
            for k in (0,1,2,0,2,3): P += q[k]
    return P
root = Node("Root", "group"); grp = Node("STL_import", "group"); root.children.append(grp)
sheet = Node("Sheet", pos=grid(20), idx=list(range(20*20*6))); grp.children.append(sheet)
other = Node("Sheet2", pos=grid(10), idx=list(range(10*10*6))); grp.children.append(other)

val = lambda x: types.SimpleNamespace(value=lambda: x, isChecked=lambda: x)
class Btn:
    def setEnabled(s, e): pass
class Lbl:
    def setText(s, t): s.t = t
class Bar:
    def setValue(s, v): pass
    def setFormat(s, f): pass
class Timer:
    on = False
    def start(s): s.on = True
    def stop(s): s.on = False
log = []
p = object.__new__(m.STLSmoothPanel)
p.__dict__.update(crease=val(40.0), tol=val(0.0), subdiv=val(0), keep=val(True), switch=val(True), label_scene=val(True),
    vrange=val(0.0), _say=log.append, _pending={}, _queue=[], _job=None, _settings=None, _reported=set(),
    _buttons=[Btn()], cancel=Btn(), progress=Bar(), _timer=Timer(), legend_lo=Lbl(), legend_mid=Lbl(), legend_hi=Lbl())
p._texture_material = lambda *a: "MAT"
def run(roots, analysis=None):
    p._smooth(roots, analysis)
    while p._timer.on: p._tick()
def tree(n, d=0):
    out = ["  "*d + n.name + (" [switch choice=%d]" % n.choice if n.kind == "switch" else "") + ("" if n.vis else " (hidden)")]
    for c in n.children: out += tree(c, d+1)
    return out
run([sheet])                                   # smooth -> switch created
p.crease = val(25.0); run([sheet])             # second smooth version
sw = sheet.parent
smooth2 = sw.children[-1]
run([smooth2], ("deviation", 20.0))            # defect map from a smoothed copy
print("\n".join(tree(root)))
names = [c.name for c in sw.children]
assert sw.kind == "switch" and sw.name == "Sheet_versions" and sw.parent is grp
assert names == ["Sheet", "Sheet_smooth_c40_s0", "Sheet_smooth_c25_s0", "Sheet_defect_dev20"], names
assert sw.choice == 3 and all(c.vis for c in sw.children)
assert other.parent is grp and other.vis, "Sheet2 must stay outside and visible"
assert len(notes) == 1 and notes[0].node is sw.children[3] and notes[0].usevis and "ORIENTATIVE" in notes[0].text
print("note:", notes[0].text.replace("\n", " | "))
print([l for l in log if "switch" in l.lower() or "ORIENTATIVE" in l][:4])
# switch off -> old hide behaviour, no new switch
p.switch = val(False); run([other])
print("switch off:", [ (c.name, c.vis) for c in grp.children])
assert other.vis is False and grp.children[-1].name == "Sheet2_smooth_c25_s0" and grp.children[-1].vis
print("OK")
# copies from an older plugin version lying next to the original get moved into the switch
old = Node("Door", pos=grid(8), idx=list(range(8*8*6))); old.vis = False; grp.children.append(old)
oldcopy = Node("Door_smooth_c40_s0", pos=grid(8), idx=list(range(8*8*6))); grp.children.append(oldcopy)
p.switch = val(True); run([old])
sw2 = old.parent
print("legacy:", sw2.name, [(c.name, c.vis) for c in sw2.children], "choice", sw2.choice)
assert sw2.name == "Door_versions" and len(sw2.children) == 3 and sw2.choice == 2 and all(c.vis for c in sw2.children)
print("OK2")
