import sys, types, importlib.util, re, math, time
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{}))
c = ns("PySide6.QtCore", Qt=base); g = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=g)),("PySide6.QtCore",c),("PySide6.QtWidgets",w),("PySide6.QtGui",g)): sys.modules[n]=m
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

# synthetic: 200x200 mm cylinder-curved panel (R=2000), 2.5 mm mesh, one Gaussian dent depth 0.3 mm sigma 5 mm at (100,100)
h = 2.5; N = 80; RC = 2000.0
def z(x, y): return (RC - math.sqrt(RC*RC - (x-100)**2)) * -1 - 0.3*math.exp(-((x-100)**2+(y-100)**2)/(2*25))
P = []
for i in range(N):
    for j in range(N):
        q = [(x*h, y*h, z(x*h, y*h)) for x, y in ((i,j),(i+1,j),(i+1,j+1),(i,j+1))]
        for k in (0,1,2,0,2,3): P += q[k]
for mode in (("deviation", 20.0), ("curvature",)):
    t0 = time.time()
    p, n, idx, st, vals = m.run_to_end(m.process(P, list(range(len(P)//3)), 40, 0, mode))
    # value at vertex nearest dent centre and far away
    best = min(range(len(p)//3), key=lambda k: (p[3*k]-100)**2+(p[3*k+1]-100)**2)
    far = [vals[k] for k in range(len(p)//3) if math.hypot(p[3*k]-100, p[3*k+1]-100) > 40 and 25 < p[3*k] < 175 and 25 < p[3*k+1] < 175]
    edge = [vals[k] for k in range(len(p)//3) if p[3*k] < 3]
    print(mode[0], "centre %.4f  far max|v| %.5f  edge max|v| %.5f  min %.4f max %.4f p98 %.4f  %.2fs"
          % (vals[best], max(map(abs, far)), max(map(abs, edge)), st["vmin"], st["vmax"], st["p98"], time.time()-t0))
    u = m.ramp_u(vals, mode[0], st["p98"])
    assert len(u) == len(p)//3 and 0 < min(u) and max(u) < 1
print("ramp", [m.ramp_color(x) for x in (0, 0.25, 0.5, 0.75, 1, 0.6)])
