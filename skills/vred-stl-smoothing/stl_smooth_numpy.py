import sys, re, numpy as np

def read_stl(p):
    b = open(p,'rb').read()
    if b[:5].lower()==b'solid' and b'facet' in b[:1000]:
        v = np.array(re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b), dtype=np.float64)
        return v.reshape(-1,3,3)
    n = int.from_bytes(b[80:84],'little')
    d = np.frombuffer(b, np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]), count=n, offset=84)
    return d['v'].reshape(-1,3,3).astype(np.float64)

def weld(tris, tol):
    pts = tris.reshape(-1,3)
    key = np.round(pts/tol).astype(np.int64)
    uniq, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return pts[idx], inv.reshape(-1,3)

def fnormals(V,F):
    a,b,c = V[F[:,0]],V[F[:,1]],V[F[:,2]]
    n = np.cross(b-a,c-a); ar = np.linalg.norm(n,axis=1)
    return n/np.maximum(ar,1e-30)[:,None], ar

def smooth(V,F,crease_deg):
    """Angle-weighted vertex normals, split corners across creases. Returns corner normals (nF,3,3)."""
    fn, ar = fnormals(V,F)
    # corner angle weights
    w = np.zeros(F.shape)
    for i in range(3):
        e1 = V[F[:,(i+1)%3]]-V[F[:,i]]; e2 = V[F[:,(i+2)%3]]-V[F[:,i]]
        cs = (e1*e2).sum(1)/np.maximum(np.linalg.norm(e1,axis=1)*np.linalg.norm(e2,axis=1),1e-30)
        w[:,i] = np.arccos(np.clip(cs,-1,1))
    cosT = np.cos(np.deg2rad(crease_deg))
    # per-vertex incident corners
    corner_v = F.reshape(-1); corner_f = np.repeat(np.arange(len(F)),3); corner_w = w.reshape(-1)
    order = np.argsort(corner_v, kind='stable')
    cv, cf, cw = corner_v[order], corner_f[order], corner_w[order]
    starts = np.r_[0, np.flatnonzero(np.diff(cv))+1, len(cv)]
    out = np.zeros((len(cv),3))
    for s,e in zip(starts[:-1],starts[1:]):
        f = fn[cf[s:e]]; ww = cw[s:e]
        sim = f@f.T >= cosT           # corners within crease angle of each other
        out[s:e] = (sim*ww[None,:])@f
    nrm = np.linalg.norm(out,axis=1,keepdims=True); out /= np.maximum(nrm,1e-30)
    res = np.zeros((len(F)*3,3)); res[order] = out
    return res.reshape(-1,3,3)

def write_obj(p,V,F,CN):
    # dedupe normals
    nn, ninv = np.unique(np.round(CN.reshape(-1,3),5), axis=0, return_inverse=True)
    ninv = ninv.reshape(-1,3)
    with open(p,'w') as f:
        f.write('# smoothed from STL\n')
        np.savetxt(f, V, fmt='v %.6f %.6f %.6f')
        np.savetxt(f, nn, fmt='vn %.5f %.5f %.5f')
        for fi,(t,nr) in enumerate(zip(F,ninv)):
            f.write('f %d//%d %d//%d %d//%d\n'%(t[0]+1,nr[0]+1,t[1]+1,nr[1]+1,t[2]+1,nr[2]+1))

if __name__=='__main__':
    src, dst = sys.argv[1], sys.argv[2]
    crease = float(sys.argv[3]) if len(sys.argv)>3 else 40
    tris = read_stl(src)
    ext = (tris.reshape(-1,3).max(0)-tris.reshape(-1,3).min(0))
    V,F = weld(tris, tol=1e-4*ext.max())
    print('triangles',len(F),'soup verts',len(F)*3,'welded verts',len(V),'extent',ext)
    ok = (F[:,0]!=F[:,1])&(F[:,1]!=F[:,2])&(F[:,0]!=F[:,2]); F=F[ok]; print('degenerate removed', (~ok).sum())
    # edge manifoldness
    e = np.sort(np.r_[F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]],axis=1)
    _,cnt = np.unique(e,axis=0,return_counts=True)
    print('edges',len(cnt),'boundary(1)',(cnt==1).sum(),'interior(2)',(cnt==2).sum(),'nonmanifold(>2)',(cnt>2).sum())
    CN = smooth(V,F,crease)
    write_obj(dst,V,F,CN)
    print('wrote',dst)
