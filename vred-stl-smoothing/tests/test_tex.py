import sys, types, importlib.util, os
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
class V3:
    def __init__(s, *a): s.a = a
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{})); c = ns("PySide6.QtCore", Qt=base); g = ns("PySide6.QtGui", QVector3D=V3)
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=g)),("PySide6.QtCore",c),("PySide6.QtWidgets",w),("PySide6.QtGui",g)): sys.modules[n]=m
sys.modules["vrKernelServices"] = ns("vrKernelServices", vrdGeometryNode=None, vrdSwitchNode=None, vrGeometryTypes=None, vrScenegraphTypes=None,
    vrMaterialTypes=types.SimpleNamespace(MaterialType=types.SimpleNamespace(Plastic="Plastic")),
    vrTextureTypes=types.SimpleNamespace(RepeatMode=types.SimpleNamespace(Repeat=1, Clamp=2), MappingType=types.SimpleNamespace(UVMapping="UV")))
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print("PLUGIN_DIR", os.path.basename(m.PLUGIN_DIR), os.path.isfile(os.path.join(m.PLUGIN_DIR, m.RAMP_FILE)))
class Img:
    def __init__(s, path): s.path = path
    def isNull(s): return False
loaded = []
m.vrImageService = types.SimpleNamespace(loadImage=lambda p: loaded.append(p) or Img(p))
class Tex:
    def __init__(s): s.img = None; s.use = False; s.map = None; s.rep = []
    def setImage(s, i): s.img = i
    def getImage(s): return s.img if s.img else types.SimpleNamespace(isNull=lambda: True)
    def setUseTexture(s, u): s.use = u
    def setMappingType(s, t): s.map = t
    def setRepeatModeU(s, r): s.rep.append(r)
    def setRepeatModeV(s, r): s.rep.append(r)
class Inc:
    def __init__(s): s.t = Tex()
    def setColor(s, c): pass
    def setIntensity(s, i): s.i = i
    def getTexture(s): return s.t
class Mat:
    def __init__(s): s.d = Tex(); s.inc = Inc()
    def isNull(s): return False
    def setDiffuseColor(s, c): pass
    def setGlossyColor(s, c): pass
    def getDiffuseTexture(s): return s.d
    def getIncandescence(s): return s.inc
mats = {}
broken = Mat(); mats["STLSmooth_DefectMap"] = broken        # material left empty by the old version
def find(n): return mats.get(n) or types.SimpleNamespace(isNull=lambda: True)
def create(n, t): mats[n] = Mat(); return mats[n]
m.vrMaterialService = types.SimpleNamespace(findMaterial=find, createMaterial=create)
log = []
p = object.__new__(m.STLSmoothPanel); p.__dict__.update(_say=log.append, _reported=set())
a = p._texture_material(m.DEFECT_MATERIAL, m.RAMP_FILE, 2, 0.5)
print("defect repaired:", a is broken, os.path.basename(a.d.img.path), a.d.use, a.d.map, a.d.rep, "| incand", os.path.basename(a.inc.t.img.path))
print("log:", log)
assert a.d.img and log == []
