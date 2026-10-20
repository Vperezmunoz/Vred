import sys, types, importlib.util, re
from PIL import Image, ImageDraw, ImageFont
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{})); c = ns("PySide6.QtCore", Qt=base); g = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=g)),("PySide6.QtCore",c),("PySide6.QtWidgets",w),("PySide6.QtGui",g)): sys.modules[n]=m
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b = open(sys.argv[2],'rb').read()
pos = [float(x) for x in re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b) for x in x]
panels = []
for mode, label in ((("deviation", 20.0), "Local deviation, defect size 20 mm"), (("deviation", 10.0), "Local deviation, defect size 10 mm"), (("curvature",), "Curvature")):
    p, n, idx, st, vals = m.run_to_end(m.process(pos, list(range(len(pos)//3)), 40, 0, mode))
    vr = st["auto"]; u = m.ramp_u(vals, mode[0], vr)
    xs, ys = p[0::3], p[1::3]; x0, y0 = min(xs), min(ys); S = 5
    W, H = int((max(xs)-x0)*S)+20, int((max(ys)-y0)*S)+60
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    for t in range(0, len(idx), 3):
        k = idx[t:t+3]; uu = sum(u[j] for j in k)/3
        d.polygon([((xs[j]-x0)*S+10, H-50-(ys[j]-y0)*S) for j in k], fill=m.ramp_color(uu))
    lo, mid, hi = m.legend_text(mode[0], vr)
    d.text((10, H-40), "%s   |   %s  ...  %s  ...  %s   |   min %.3f  max %.3f" % (label, lo, mid, hi, st["vmin"], st["vmax"]), fill="black")
    for x in range(300): d.line([(10+x, H-22), (10+x, H-10)], fill=m.ramp_color(x/299))
    panels.append(img)
W = max(i.width for i in panels); out = Image.new("RGB", (W, sum(i.height for i in panels)), "white"); y = 0
for i in panels: out.paste(i, (0, y)); y += i.height
out.save(sys.argv[3]); print(out.size)
