import sys, types, importlib.util
from PIL import Image
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{})); c = ns("PySide6.QtCore", Qt=base); g = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=g)),("PySide6.QtCore",c),("PySide6.QtWidgets",w),("PySide6.QtGui",g)): sys.modules[n]=m
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ramp = Image.new("RGB", (256, 4))
for x in range(256):
    for y in range(4): ramp.putpixel((x, y), m.ramp_color(x / 255.0))
ramp.save(sys.argv[2] + "/" + m.RAMP_FILE)
st = Image.new("RGB", (64, 4))
for x in range(64):
    for y in range(4): st.putpixel((x, y), (0, 0, 0) if x < 32 else (255, 255, 255))
st.save(sys.argv[2] + "/" + m.STRIPE_FILE)
print(m.RAMP_FILE, m.STRIPE_FILE)
