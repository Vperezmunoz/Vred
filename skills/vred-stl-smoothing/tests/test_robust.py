import sys, types, importlib.util, re, time, random, math
def ns(name, **a):
    m = types.ModuleType(name); [setattr(m,k,v) for k,v in a.items()]; return m
base = type("Stub",(object,),{})
w = ns("PySide6.QtWidgets", QWidget=type("QWidget",(base,),{}))
c = ns("PySide6.QtCore", Qt=base); gq = ns("PySide6.QtGui")
for n,m in (("PySide6",ns("PySide6",QtCore=c,QtWidgets=w,QtGui=gq)),("PySide6.QtGui",gq),("PySide6.QtCore",c),("PySide6.QtWidgets",w)): sys.modules[n]=m
spec = importlib.util.spec_from_file_location("m", sys.argv[2]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def check(pos, idx, label, ref_up=None):
    t0 = time.time(); nyield = 0; gen = m.process(pos, idx, 40.0, 0.0); last=-1
    while True:
        try: stage, f = next(gen); nyield += 1; assert f >= last - 1e-9 and f <= 1.0001, (stage, f, last); last = f
        except StopIteration as s: res = s.value; break
    p, n, i, st, _ = res
    dt = time.time() - t0
    # each triangle's stored normals must agree with its winding
    bad = 0; down = 0
    for t in range(0, len(i), 3):
        a, b, cc = [p[3*k:3*k+3] for k in i[t:t+3]]
        fn = m._unit(m._cross(m._sub(b, a), m._sub(cc, a)))
        if ref_up is not None and m._dot(fn, ref_up) < 0: down += 1
        for k in i[t:t+3]:
            if m._dot(fn, n[3*k:3*k+3]) < 0.5: bad += 1
    print("%-28s tris %7d flipped %6d patches %d conflicts %d bad-corners %d down-facing %d yields %d  %.2fs"
          % (label, st["tris"], st["flipped"], st["patches"], st["conflicts"], bad, down, nyield, dt))
    return st, down

b = open(sys.argv[1],'rb').read()
pos = [float(x) for x in re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b) for x in x]
idx = list(range(len(pos)//3))
st, _ = check(pos, idx, "sample as exported", (0,0,1))
assert st["flipped"] == 0

# flip 30% of sample triangles (swap 2nd/3rd corner)
random.seed(1); bad_idx = list(idx); nflip = 0
for t in range(0, len(bad_idx), 3):
    if random.random() < 0.3: bad_idx[t+1], bad_idx[t+2] = bad_idx[t+2], bad_idx[t+1]; nflip += 1
st, down = check(pos, bad_idx, "sample, 30%% flipped (%d)" % nflip, (0,0,1))
assert st["flipped"] == nflip and down == 0 and st["conflicts"] == 0

# 70% flipped: majority wins, so whole patch ends up facing down consistently
bad2 = list(idx); n2 = 0
for t in range(0, len(bad2), 3):
    if random.random() < 0.7: bad2[t+1], bad2[t+2] = bad2[t+2], bad2[t+1]; n2 += 1
st, down = check(pos, bad2, "sample, 70%% flipped (%d)" % n2, (0,0,1))
assert down in (0, st["tris"]), down

# large synthetic: wavy sheet as triangle soup
def soup(N):
    P = []; 
    f = lambda x, y: (x, y, 3*math.sin(x*0.05)*math.cos(y*0.04))
    for i in range(N):
        for j in range(N):
            a, b2, c2, d = f(i,j), f(i+1,j), f(i+1,j+1), f(i,j+1)
            P += [*a, *b2, *c2, *a, *c2, *d]
    return P
for N in (300, 710):
    P = soup(N); check(P, list(range(len(P)//3)), "synthetic %dk tris" % (2*N*N//1000))
