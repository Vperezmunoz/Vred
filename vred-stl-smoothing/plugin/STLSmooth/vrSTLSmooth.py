"""STLSmooth - VRED script plugin.

Not a product of Autodesk. Not developed, endorsed, supported or warranted by Autodesk.
Provided "as is", without warranty of any kind. See DISCLAIMER.txt.

STL files store every triangle separately (no shared vertices, one flat normal per face),
so VRED renders them faceted. This plugin welds coincident vertices back together, makes
the triangle orientation consistent, and computes smooth per-vertex normals with a crease
angle. By default it smooths an independent copy (<part>_smooth_c<crease>_s<subdiv>) and
puts the original and every copy of the part into one switch node (<part>_versions), so
versions can be compared by switching; optionally it replaces in place.

    Scripts > STLSmooth
        Import STL...         import one or more STL files, then smooth them
        Import STL folder...  import every *.stl in a folder, then smooth them
        Smooth selected       smooth geometry already in the scene (selection + children)
        Defect map selected   coloured copy by local deviation (mm) or curvature

VRED's bundled Python has no numpy, so the mesh maths below is pure Python. Each step is
a generator that yields its progress, so the panel can run it in short time slices and
keep VRED responsive on large meshes.
"""

import math
import os
import time

from PySide6 import QtCore, QtGui, QtWidgets

try:
    from vrKernelServices import (vrdGeometryNode, vrdSwitchNode, vrGeometryTypes,
                                  vrScenegraphTypes, vrMaterialTypes, vrTextureTypes)
except ImportError:
    vrdGeometryNode = vrdSwitchNode = vrGeometryTypes = vrScenegraphTypes = None
    vrMaterialTypes = vrTextureTypes = None

SMOOTH_TAG = "_smooth_c"               # name marker of smoothed copies made by this plugin
DEFECT_TAG = "_defect_"                # name marker of defect-map copies
RESULT_TAGS = (SMOOTH_TAG, DEFECT_TAG)
SWITCH_SUFFIX = "_versions"            # switch node holding a part's original and copies
ORIENTATIVE = ("ORIENTATIVE ONLY - estimated from the mesh geometry, not a CAE result. "
               "Shows where to look, not how much; values will differ from the stamping "
               "simulation's own results.")
DEFECT_MATERIAL = "STLSmooth_DefectMap"
RAMP_FILE = "STLSmooth_ramp.png"       # colour-ramp texture shipped next to this file
try:
    PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    PLUGIN_DIR = os.getcwd()
# colour ramp stops (position, r, g, b): blue - cyan - green - yellow - red
RAMP = ((0.0, 0, 0, 255), (0.25, 0, 220, 255), (0.5, 0, 200, 0),
        (0.75, 255, 230, 0), (1.0, 255, 0, 0))
YIELD_EVERY = 20000                    # items between progress reports
SLICE_SECONDS = 0.05                   # work per UI tick before VRED gets control back


# --------------------------------------------------------------------------- mesh maths
# Every step is a generator: it yields a fraction 0..1 now and then, and returns its
# result (read it with `result = yield from step(...)`, or run_to_end() outside the UI).

def run_to_end(gen):
    """Drive a step generator without a UI and return its result."""
    while True:
        try:
            next(gen)
        except StopIteration as stop:
            return stop.value


def weld(positions, indices, tol):
    """Merge vertices closer than `tol`. Returns (points, triangles) with shared indices.
    positions: flat [x,y,z,...]; indices: flat triangle list (len % 3 == 0)."""
    inv = 1.0 / tol
    key_to_new = {}
    points = []
    nverts = len(positions) // 3
    remap = [0] * nverts
    for i in range(nverts):
        x, y, z = positions[3*i], positions[3*i+1], positions[3*i+2]
        k = (round(x * inv), round(y * inv), round(z * inv))
        j = key_to_new.get(k)
        if j is None:
            j = len(points)
            key_to_new[k] = j
            points.append((x, y, z))
        remap[i] = j
        if i % YIELD_EVERY == 0:
            yield 0.7 * i / nverts
    tris = []
    ntri = len(indices) // 3
    for f in range(ntri):
        t = 3 * f
        a, b, c = remap[indices[t]], remap[indices[t+1]], remap[indices[t+2]]
        if a != b and b != c and a != c:          # drop triangles collapsed by the weld
            tris.append((a, b, c))
        if f % YIELD_EVERY == 0:
            yield 0.7 + 0.3 * f / ntri
    return points, tris


def edge_faces(tris):
    """Undirected edge (lo, hi) -> list of faces using it."""
    ef = {}
    for f, (a, b, c) in enumerate(tris):
        for u, v in ((a, b), (b, c), (c, a)):
            e = (u, v) if u < v else (v, u)
            lst = ef.get(e)
            if lst is None:
                ef[e] = [f]
            else:
                lst.append(f)
        if f % YIELD_EVERY == 0:
            yield 0.4 * f / max(len(tris), 1)
    return ef


def _has_directed(t, u, v):
    return ((t[0] == u and t[1] == v) or (t[1] == u and t[2] == v)
            or (t[2] == u and t[0] == v))


def orient(tris):
    """Make neighbouring triangles agree on winding (and so on normal direction).

    Walks each connected patch across edges shared by exactly two faces and flips any
    face whose winding disagrees with its neighbour. Within each patch the majority
    winding of the input is kept, so a mostly-correct export keeps its outside side.
    Returns (tris, stats)."""
    ef = yield from edge_faces(tris)
    n = len(tris)
    out = list(tris)
    done = [False] * n
    flipped = 0
    patches = 0
    conflicts = 0                      # edges no flip can fix (e.g. Moebius-like strips)
    visited = 0
    for seed in range(n):
        if done[seed]:
            continue
        patches += 1
        done[seed] = True
        patch, flips = [seed], []
        stack = [seed]
        while stack:
            f = stack.pop()
            t = out[f]
            for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                faces = ef[(u, v) if u < v else (v, u)]
                if len(faces) != 2:
                    continue           # boundary or non-manifold: don't propagate
                g = faces[1] if faces[0] == f else faces[0]
                if done[g]:
                    if _has_directed(out[g], u, v):
                        conflicts += 1
                    continue
                done[g] = True
                if _has_directed(out[g], u, v):      # same direction as f: flip g
                    a, b, c = out[g]
                    out[g] = (a, c, b)
                    flips.append(g)
                patch.append(g)
                stack.append(g)
            visited += 1
            if visited % YIELD_EVERY == 0:
                yield 0.4 + 0.6 * visited / n
        if 2 * len(flips) > len(patch):
            # the seed was the odd one out: flip the whole patch back to the majority
            flipped_set = set(flips)
            for f in patch:
                a, b, c = out[f]
                out[f] = (a, c, b)
            flipped += len(patch) - len(flipped_set)
        else:
            flipped += len(flips)
    boundary = sum(1 for faces in ef.values() if len(faces) == 1)
    nonmanifold = sum(1 for faces in ef.values() if len(faces) > 2)
    return out, dict(flipped=flipped, patches=patches, conflicts=conflicts // 2,
                     boundary=boundary, nonmanifold=nonmanifold)


def _sub(p, q):
    return (p[0]-q[0], p[1]-q[1], p[2]-q[2])


def _cross(u, v):
    return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])


def _dot(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]


def _unit(v):
    n = math.sqrt(_dot(v, v))
    return (v[0]/n, v[1]/n, v[2]/n) if n > 1e-30 else (0.0, 0.0, 1.0)


def smooth_normals(points, tris, crease_deg):
    """Angle-weighted vertex normals. A corner only averages with neighbouring faces whose
    normal is within `crease_deg` of its own face, so real sharp edges stay sharp.
    Returns flat (positions, normals, indices) ready for vrdGeometryNode; vertices on a
    crease are duplicated, one copy per normal."""
    ntri = max(len(tris), 1)
    fnorm, cw = [], []                 # face normals, corner angle weights
    for f, (a, b, c) in enumerate(tris):
        pa, pb, pc = points[a], points[b], points[c]
        fnorm.append(_unit(_cross(_sub(pb, pa), _sub(pc, pa))))
        w = []
        for p, q, r in ((pa, pb, pc), (pb, pc, pa), (pc, pa, pb)):
            e1, e2 = _unit(_sub(q, p)), _unit(_sub(r, p))
            w.append(math.acos(max(-1.0, min(1.0, _dot(e1, e2)))))
        cw.append(w)
        if f % YIELD_EVERY == 0:
            yield 0.25 * f / ntri

    incident = [[] for _ in points]    # vertex -> [(face, corner)]
    for f, t in enumerate(tris):
        for k in range(3):
            incident[t[k]].append((f, k))

    cos_t = math.cos(math.radians(crease_deg))
    corner_n = [[None] * 3 for _ in tris]
    nv = max(len(incident), 1)
    for vi, corners in enumerate(incident):
        for f, k in corners:
            nf = fnorm[f]
            sx = sy = sz = 0.0
            for g, m in corners:
                ng = fnorm[g]
                if _dot(nf, ng) >= cos_t:
                    w = cw[g][m]
                    sx += ng[0]*w; sy += ng[1]*w; sz += ng[2]*w
            corner_n[f][k] = _unit((sx, sy, sz))
        if vi % YIELD_EVERY == 0:
            yield 0.3 + 0.5 * vi / nv

    out_p, out_n, out_i, seen = [], [], [], {}
    out_src = []                       # welded vertex behind each output vertex
    for f, t in enumerate(tris):
        for k in range(3):
            n = corner_n[f][k]
            key = (t[k], round(n[0], 4), round(n[1], 4), round(n[2], 4))
            j = seen.get(key)
            if j is None:
                j = len(seen)
                seen[key] = j
                out_p.extend(points[t[k]])
                out_n.extend(n)
                out_src.append(t[k])
            out_i.append(j)
        if f % YIELD_EVERY == 0:
            yield 0.8 + 0.2 * f / ntri
    return out_p, out_n, out_i, out_src


def auto_tolerance(positions):
    lo = [min(positions[i::3]) for i in range(3)]
    hi = [max(positions[i::3]) for i in range(3)]
    return max(1e-4 * max(h - l for h, l in zip(hi, lo)), 1e-9)


# --------------------------------------------------------------------------- defect map

def vertex_normals(points, tris):
    """Area-weighted vertex normals with no crease - one normal per welded vertex."""
    acc = [[0.0, 0.0, 0.0] for _ in points]
    for a, b, c in tris:
        n = _cross(_sub(points[b], points[a]), _sub(points[c], points[a]))
        for v in (a, b, c):
            s = acc[v]
            s[0] += n[0]; s[1] += n[1]; s[2] += n[2]
    return [_unit(s) for s in acc]


def deviation_values(points, tris, radius):
    """Signed distance (scene units, i.e. mm) of each vertex from a smoothed version of
    the part, measured along the vertex normal. + = bump outward, - = dent inward.

    The smooth reference is a biweight-weighted average of the surface within `radius`.
    To keep the cost independent of the radius, the surface is first binned into cells
    of radius/4 and the average is taken over the cell centroids. Shapes much larger
    than the radius (the panel's design form) cancel out; dents, buckles and wrinkles
    up to about the radius show up."""
    normals = vertex_normals(points, tris)
    bin_size = radius / 4.0
    bins = {}
    for x, y, z in points:
        k = (int(math.floor(x / bin_size)), int(math.floor(y / bin_size)),
             int(math.floor(z / bin_size)))
        s = bins.get(k)
        if s is None:
            bins[k] = [x, y, z, 1]
        else:
            s[0] += x; s[1] += y; s[2] += z; s[3] += 1
    cells = {}                         # radius-sized cell -> [(cx, cy, cz, count)]
    for sx, sy, sz, cnt in bins.values():
        cx, cy, cz = sx / cnt, sy / cnt, sz / cnt
        k = (int(math.floor(cx / radius)), int(math.floor(cy / radius)),
             int(math.floor(cz / radius)))
        cells.setdefault(k, []).append((cx, cy, cz, cnt))
    yield 0.05

    r2 = radius * radius
    inv_r2 = 1.0 / r2
    n = max(len(points), 1)
    values = [0.0] * len(points)
    for i, (x, y, z) in enumerate(points):
        kx, ky, kz = (int(math.floor(x / radius)), int(math.floor(y / radius)),
                      int(math.floor(z / radius)))
        sw = mx = my = mz = 0.0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    lst = cells.get((kx + dx, ky + dy, kz + dz))
                    if lst is None:
                        continue
                    for cx, cy, cz, cnt in lst:
                        ex, ey, ez = cx - x, cy - y, cz - z
                        d2 = ex*ex + ey*ey + ez*ez
                        if d2 < r2:
                            t = 1.0 - d2 * inv_r2
                            w = t * t * cnt
                            sw += w; mx += w*cx; my += w*cy; mz += w*cz
        if sw > 0.0:
            nx, ny, nz = normals[i]
            values[i] = (x - mx/sw)*nx + (y - my/sw)*ny + (z - mz/sw)*nz
        if i % 5000 == 0:
            yield 0.05 + 0.95 * i / n
    return values


def curvature_values(points, tris):
    """Unsigned curvature (1/scene unit) per vertex from the change of normal along each
    edge: |(n_i - n_j) . (p_i - p_j)| / |p_i - p_j|^2, averaged over the vertex's edges.
    1/value is the local bending radius."""
    normals = vertex_normals(points, tris)
    acc = [0.0] * len(points)
    cnt = [0] * len(points)
    seen = set()
    nt = max(len(tris), 1)
    for f, (a, b, c) in enumerate(tris):
        for u, v in ((a, b), (b, c), (c, a)):
            e = (u, v) if u < v else (v, u)
            if e in seen:
                continue
            seen.add(e)
            d = _sub(points[u], points[v])
            l2 = _dot(d, d)
            if l2 <= 0.0:
                continue
            k = abs(_dot(_sub(normals[u], normals[v]), d)) / l2
            acc[u] += k; acc[v] += k
            cnt[u] += 1; cnt[v] += 1
        if f % YIELD_EVERY == 0:
            yield f / nt
    return [s / c if c else 0.0 for s, c in zip(acc, cnt)]


def percentile(values, q):
    s = sorted(values)
    if not s:
        return 0.0
    return s[min(len(s) - 1, int(q * (len(s) - 1) + 0.5))]


def ramp_u(values, mode, value_range):
    """Map per-vertex values to the U texture coordinate of the colour ramp.
    deviation: -range..+range -> 0..1 (0 mm = middle); curvature: 0..range -> 0..1."""
    lo, hi = 0.004, 0.996              # stay off the ramp's outermost texels
    if mode == "deviation":
        return [min(hi, max(lo, 0.5 + 0.5 * v / value_range)) for v in values]
    return [min(hi, max(lo, v / value_range)) for v in values]


def process(positions, indices, crease_deg, tol, analysis=None):
    """Full pipeline as one generator yielding (stage, fraction). Returns
    (positions, normals, indices, stats, values) or None for an empty mesh; `values` is
    one analysis value per output vertex, or None.

    analysis: None, ("deviation", radius) or ("curvature",)."""
    if len(indices) < 3:
        return None
    tol = tol if tol > 0 else auto_tolerance(positions)
    if analysis is None:
        weights = (0.20, 0.25, 0.55, 0.0)
    elif analysis[0] == "deviation":
        weights = (0.10, 0.12, 0.28, 0.50)
    else:
        weights = (0.15, 0.20, 0.45, 0.20)
    progress = [0.0]

    def staged(gen, name, weight):
        while True:
            try:
                frac = next(gen)
            except StopIteration as stop:
                progress[0] += weight
                return stop.value
            yield name, progress[0] + weight * frac

    points, tris = yield from staged(weld(positions, indices, tol), "welding", weights[0])
    tris, stats = yield from staged(orient(tris), "orienting", weights[1])
    p, n, i, src = yield from staged(smooth_normals(points, tris, crease_deg),
                                     "normals", weights[2])
    stats.update(tris=len(tris), before=len(positions) // 3, welded=len(points),
                 out=len(p) // 3, tol=tol)
    values = None
    if analysis is not None:
        if analysis[0] == "deviation":
            per_vertex = yield from staged(deviation_values(points, tris, analysis[1]),
                                           "deviation", weights[3])
        else:
            per_vertex = yield from staged(curvature_values(points, tris),
                                           "curvature", weights[3])
        values = [per_vertex[s] for s in src]
        mags = [abs(v) for v in per_vertex]
        # auto colour range: deviation - the strongest defects (99.9th percentile, so
        # one stray vertex can't wash out the map); curvature - 98th percentile, since
        # intended design radii cover a larger share of the part
        q = 0.999 if analysis[0] == "deviation" else 0.98
        stats.update(vmin=min(per_vertex), vmax=max(per_vertex),
                     p98=percentile(mags, 0.98), auto=percentile(mags, q))
    return p, n, i, stats, values


# --------------------------------------------------------------------------- VRED side

def geometry_nodes(roots):
    """Triangle geometry under the given nodes (deduplicated, roots included)."""
    found, seen = [], set()
    for root in roots:
        for node in root.getChildrenRecursive(True, False):
            if not node.isType(vrdGeometryNode):
                continue
            geo = vrdGeometryNode(node)
            if geo.getPrimitiveType() != vrGeometryTypes.PrimitiveType.Triangles:
                continue
            key = geo.getObjectId()
            if key not in seen:
                seen.add(key)
                found.append(geo)
    return found




def is_result(name):
    return any(tag in name for tag in RESULT_TAGS)


def source_name(name):
    """Name of the original part behind a result copy (the name itself otherwise)."""
    for tag in RESULT_TAGS:
        k = name.find(tag)
        if k > 0:
            return name[:k]
    return name


def ramp_color(u):
    """RGB (0..255) of the colour ramp at u in 0..1."""
    u = min(1.0, max(0.0, u))
    for (u0, r0, g0, b0), (u1, r1, g1, b1) in zip(RAMP, RAMP[1:]):
        if u <= u1:
            t = (u - u0) / (u1 - u0)
            return (int(r0 + t*(r1-r0) + 0.5), int(g0 + t*(g1-g0) + 0.5),
                    int(b0 + t*(b1-b0) + 0.5))
    return RAMP[-1][1:]


def ramp_image(width=256, height=4):
    img = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
    for x in range(width):
        c = QtGui.QColor(*ramp_color(x / (width - 1.0)))
        for y in range(height):
            img.setPixelColor(x, y, c)
    return img


def stats_line(name, s, seconds):
    line = ("%s: %d tris, %d -> %d welded verts, %d out, boundary %d, non-manifold %d, "
            "tol %.2g, %.1f s" % (name, s["tris"], s["before"], s["welded"], s["out"],
                                  s["boundary"], s["nonmanifold"], s["tol"], seconds))
    if s["flipped"]:
        line += "\n    repaired orientation of %d triangle(s)" % s["flipped"]
    if s["conflicts"]:
        line += ("\n    WARNING %d edge(s) could not be made consistent - check that "
                 "area for dark seams" % s["conflicts"])
    if s["patches"] > 1:
        line += "\n    %d separate patches" % s["patches"]
    return line


def legend_text(mode, value_range):
    if mode == "deviation":
        return ("approx. -%.3g mm (dent)" % value_range, "0",
                "approx. +%.3g mm (bump)" % value_range)
    return ("flat", "", "approx. >= %.3g /mm (radius %.3g mm)"
            % (value_range, 1.0 / value_range))


class STLSmoothPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is not None:
            layout = parent.layout() or QtWidgets.QVBoxLayout(parent)
            layout.addWidget(self)
        self._pending = {}             # importId -> root children before the import
        self._queue = []               # geometry nodes waiting to be processed
        self._job = None               # (geo, generator, start time) being processed
        self._settings = None          # settings frozen when a run starts
        self._reported = set()         # API calls whose failure was already logged
        self._build_ui()
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(0)
        self._timer.timeout.connect(self._tick)
        vrFileIOService.importFinished.connect(self._on_import_finished)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        v = QtWidgets.QVBoxLayout(self)
        v.addWidget(self._build_smooth_box())
        v.addWidget(self._build_defect_box())

        prow = QtWidgets.QHBoxLayout()
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("idle")
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self._cancel)
        prow.addWidget(self.progress)
        prow.addWidget(self.cancel)
        v.addLayout(prow)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        v.addWidget(self.log)

        note = QtWidgets.QLabel("Not an Autodesk product. Provided as is, without warranty.")
        note.setStyleSheet("color: gray; font-size: 8pt;")
        v.addWidget(note)

    def _build_smooth_box(self):
        box = QtWidgets.QGroupBox("Smooth")
        v = QtWidgets.QVBoxLayout(box)
        form = QtWidgets.QFormLayout()
        self.crease = QtWidgets.QDoubleSpinBox()
        self.crease.setRange(0.0, 180.0)
        self.crease.setValue(40.0)
        self.crease.setSuffix(" deg")
        self.crease.setToolTip("Faces meeting at more than this angle keep a hard edge.\n"
                               "Raise to smooth more, lower to keep more edges.")
        form.addRow("Crease angle", self.crease)

        self.tol = QtWidgets.QDoubleSpinBox()
        self.tol.setDecimals(5)
        self.tol.setRange(0.0, 10.0)
        self.tol.setSingleStep(0.001)
        self.tol.setValue(0.0)
        self.tol.setSpecialValueText("auto")
        self.tol.setSuffix(" scene units")
        self.tol.setToolTip("Vertices closer than this are merged. 'auto' = 0.01% of the\n"
                            "part's largest dimension. Increase if seams remain.")
        form.addRow("Weld tolerance", self.tol)

        self.subdiv = QtWidgets.QSpinBox()
        self.subdiv.setRange(0, 3)
        self.subdiv.setToolTip("Phong subdivision passes after smoothing. Rounds off a\n"
                               "faceted silhouette; each pass ~4x the triangles.")
        form.addRow("Subdivision", self.subdiv)

        self.keep = QtWidgets.QCheckBox("Keep original (smooth a copy)")
        self.keep.setChecked(True)
        self.keep.setToolTip("Smooth an independent duplicate named <part>_smooth_c40_s0\n"
                             "and leave the original STL untouched, so you can run again\n"
                             "with other settings. Unchecked: replace the original in place.")
        self.switch = QtWidgets.QCheckBox("Compare in a switch node")
        self.switch.setChecked(True)
        self.switch.setToolTip("Put the original and every copy of the part into one switch\n"
                               "node <part>_versions and show the newest. Pick another version\n"
                               "in the Scenegraph (or a variant set) to compare.\n"
                               "Unchecked: copies sit next to the original, which is hidden.")
        self.keep.toggled.connect(self.switch.setEnabled)
        form.addRow(self.keep)
        form.addRow(self.switch)
        v.addLayout(form)

        row = QtWidgets.QHBoxLayout()
        self._buttons = []
        for text, slot in (("Import STL...", self._import_files),
                           ("Import folder...", self._import_folder),
                           ("Smooth selected", self._smooth_selected)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(slot)
            row.addWidget(b)
            self._buttons.append(b)
        v.addLayout(row)
        return box

    def _build_defect_box(self):
        box = QtWidgets.QGroupBox("Defect colour map")
        v = QtWidgets.QVBoxLayout(box)
        form = QtWidgets.QFormLayout()
        self.dmode = QtWidgets.QComboBox()
        self.dmode.addItem("Local deviation (approx. mm)", "deviation")
        self.dmode.addItem("Curvature", "curvature")
        self.dmode.setToolTip("Local deviation: how far each point sits above/below a smoothed\n"
                              "version of the part - shows dents, buckles, wrinkles.\n"
                              "Curvature: how sharply the surface bends - also shows design\n"
                              "features such as beads and radii.")
        form.addRow("Mode", self.dmode)

        self.radius = QtWidgets.QDoubleSpinBox()
        self.radius.setRange(1.0, 1000.0)
        self.radius.setValue(20.0)
        self.radius.setSuffix(" mm")
        self.radius.setToolTip("Size of the smoothed reference. Defects up to about this size\n"
                               "show; larger shapes count as the part's design form.")
        form.addRow("Defect size", self.radius)

        self.vrange = QtWidgets.QDoubleSpinBox()
        self.vrange.setDecimals(3)
        self.vrange.setRange(0.0, 1000.0)
        self.vrange.setSingleStep(0.05)
        self.vrange.setSpecialValueText("auto")
        self.vrange.setToolTip("Value at full blue/red. Deviation: +/- mm. Curvature: the\n"
                               "smallest bending radius in mm that shows full red.\n"
                               "auto = scaled to the strongest defects of this part. Use a\n"
                               "fixed value to compare several parts on the same scale.")
        form.addRow("Colour range", self.vrange)
        self.label_scene = QtWidgets.QCheckBox("Label maps as orientative in the scene")
        self.label_scene.setChecked(True)
        self.label_scene.setToolTip("Adds a VRED annotation to each defect map saying it is an\n"
                                    "orientative estimate, not a CAE result - it shows in the\n"
                                    "viewport and in screenshots.")
        form.addRow(self.label_scene)
        self.dmode.currentIndexChanged.connect(self._defect_mode_changed)
        self._defect_mode_changed()
        v.addLayout(form)

        b = QtWidgets.QPushButton("Defect map selected")
        b.setToolTip("Always makes a new copy named <part>_defect_..., the original is\n"
                     "never changed.")
        b.clicked.connect(self._defect_selected)
        self._buttons.append(b)
        v.addWidget(b)

        self.legend = QtWidgets.QLabel()
        self.legend.setPixmap(QtGui.QPixmap.fromImage(ramp_image().scaled(240, 12)))
        self.legend.setAlignment(QtCore.Qt.AlignCenter)
        v.addWidget(self.legend)
        lrow = QtWidgets.QHBoxLayout()
        self.legend_lo, self.legend_mid, self.legend_hi = (QtWidgets.QLabel("-"),
                                                           QtWidgets.QLabel(""),
                                                           QtWidgets.QLabel("+"))
        self.legend_mid.setAlignment(QtCore.Qt.AlignCenter)
        self.legend_hi.setAlignment(QtCore.Qt.AlignRight)
        for w in (self.legend_lo, self.legend_mid, self.legend_hi):
            lrow.addWidget(w)
        v.addLayout(lrow)
        note = QtWidgets.QLabel(ORIENTATIVE)
        note.setWordWrap(True)
        note.setStyleSheet("color: #c06000; font-size: 8pt;")
        v.addWidget(note)
        return box

    def _defect_mode_changed(self, *_):
        dev = self.dmode.currentData() == "deviation"
        self.radius.setEnabled(dev)
        self.vrange.setSuffix(" mm" if dev else " mm radius")

    def _say(self, msg):
        self.log.appendPlainText(msg)
        print("[STLSmooth] " + msg)

    def _call(self, label, fn, *args):
        """Call a VRED function; log the first failure of each call instead of raising."""
        try:
            fn(*args)
            return True
        except Exception as exc:
            if label not in self._reported:
                self._reported.add(label)
                self._say("%s failed: %s: %s" % (label, type(exc).__name__, exc))
            return False

    # ------------------------------------------------------------------ import
    def _import_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Import STL", "", "STL files (*.stl *.STL)")
        self._start_import(files)

    def _import_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Folder with STL files")
        if folder:
            files = sorted(os.path.join(folder, f) for f in os.listdir(folder)
                           if f.lower().endswith(".stl"))
            if not files:
                self._say("No .stl files in " + folder)
            self._start_import(files)

    def _start_import(self, files):
        if not files:
            return
        root = vrScenegraphService.getRootNode()
        before = {c.getObjectId() for c in root.getChildren()}
        import_id = vrFileIOService.importFiles(files, root)
        self._pending[import_id] = before
        self._say("Importing %d file(s)..." % len(files))

    def _on_import_finished(self, import_id, duration):
        before = self._pending.pop(import_id, None)
        if before is None:
            return                     # someone else's import
        root = vrScenegraphService.getRootNode()
        new = [c for c in root.getChildren() if c.getObjectId() not in before]
        self._say("Import done in %.1f s, %d new node(s)." % (duration, len(new)))
        self._smooth(new)

    # ------------------------------------------------------------------ runs
    def _selected_or_warn(self):
        nodes = vrNodeService.getSelectedNodes()
        if not nodes:
            self._say("Select one or more nodes in the Scenegraph first.")
        return nodes

    def _smooth_selected(self):
        nodes = self._selected_or_warn()
        if nodes:
            self._smooth(nodes)

    def _defect_selected(self):
        try:
            nodes = self._selected_or_warn()
            if not nodes:
                return
            if self.dmode.currentData() == "deviation":
                analysis = ("deviation", self.radius.value())
            else:
                analysis = ("curvature",)
            self._smooth(nodes, analysis)
        except Exception as exc:       # a slot error would otherwise only reach the Terminal
            self._say("Defect map FAILED %s: %s" % (type(exc).__name__, exc))

    def _smooth(self, roots, analysis=None):
        if self._job is not None or self._queue:
            self._say("Still processing - wait for it to finish or press Cancel.")
            return
        geos = geometry_nodes(roots)
        if not geos:
            self._say("No triangle geometry found.")
            return
        keep = self.keep.isChecked() or analysis is not None   # analysis always copies
        if keep:
            # copies made earlier are results, not sources - don't copy them again. A
            # smoothed copy is a fine source for a defect map, though.
            skip = (lambda n: DEFECT_TAG in n) if analysis is not None else is_result
            skipped = [g for g in geos if skip(g.getName())]
            geos = [g for g in geos if not skip(g.getName())]
            if skipped:
                self._say("Skipped %d earlier result copies: %s"
                          % (len(skipped), ", ".join(g.getName() for g in skipped[:5])))
            if analysis is not None:
                # one result per part: if the original and its smoothed copy are both
                # selected, use the original
                by_part = {}
                for g in geos:
                    base = source_name(g.getName())
                    if base not in by_part or g.getName() == base:
                        by_part[base] = g
                geos = [g for g in geos if by_part.get(source_name(g.getName())) is g]
            if not geos:
                self._say("Nothing to do - select the original STL or its _smooth_ copy.")
                return
        what = {None: "Smoothing", "deviation": "Defect map (deviation)",
                "curvature": "Defect map (curvature)"}
        self._say("%s: %d part(s) queued." % (what[analysis[0] if analysis else None],
                                              len(geos)))
        self._settings = dict(crease=self.crease.value(), tol=self.tol.value(),
                              subdiv=self.subdiv.value(), keep=keep,
                              switch=self.switch.isChecked() or not self.keep.isChecked(),
                              label=self.label_scene.isChecked(),
                              analysis=analysis, vrange=self.vrange.value())
        self._queue = list(geos)
        self._total = len(geos)
        self._set_running(True)
        self._timer.start()

    def _set_running(self, running):
        for b in self._buttons:
            b.setEnabled(not running)
        self.cancel.setEnabled(running)
        if not running:
            self.progress.setValue(0)
            self.progress.setFormat("idle")

    def _tick(self):
        """Run the current job for one time slice, then hand control back to VRED."""
        name = self._job[0].getName() if self._job else "?"
        try:
            if self._job is None:
                if not self._queue:
                    self._finish()
                    return
                geo = self._queue.pop(0)
                s = self._settings
                gen = process(list(geo.getPositions()), list(geo.getIndices()),
                              s["crease"], s["tol"], s["analysis"])
                self._job = (geo, gen, time.time())
            geo, gen, t0 = self._job
            name = geo.getName()
            done = self._total - len(self._queue) - 1
            deadline = time.time() + SLICE_SECONDS
            while True:                # always at least one step, even on a slow tick
                try:
                    stage, frac = next(gen)
                except StopIteration as stop:
                    self._job = None
                    if stop.value is not None:
                        self._apply(geo, stop.value, time.time() - t0)
                    return
                if time.time() >= deadline:
                    break
            self.progress.setValue(int(1000 * (done + frac) / self._total))
            self.progress.setFormat("%d/%d  %s  %s  %%p%%"
                                    % (done + 1, self._total, geo.getName(), stage))
        except Exception as exc:
            self._say("%s: FAILED %s: %s" % (name, type(exc).__name__, exc))
            self._job = None

    def _result_name(self, src):
        s = self._settings
        a = s["analysis"]
        if a is None:
            return "%s%s%g_s%d" % (src.getName(), SMOOTH_TAG, s["crease"], s["subdiv"])
        base = source_name(src.getName())
        if a[0] == "deviation":
            return "%s%sdev%g" % (base, DEFECT_TAG, a[1])
        return "%s%scurv" % (base, DEFECT_TAG)

    def _apply(self, src, result, seconds):
        """Write the result to the scene: onto a fresh copy, or onto `src` itself."""
        p, n, i, stats, values = result
        s = self._settings
        geo = src
        switch = None
        if s["keep"]:
            if s["switch"]:
                switch = self._part_switch(src)   # moves src (and old copies) inside
            dup = vrScenegraphService.duplicateNodes(
                [src], vrScenegraphTypes.DuplicateOption.DuplicateAll)[0]
            geo = vrdGeometryNode(dup)
            geo.setName(self._result_name(src))
            if switch is None:
                src.setVisibilityFlag(False)
                # the original and earlier copies of this part would overlap the new one
                base = source_name(src.getName())
                prefixes = tuple(base + tag for tag in RESULT_TAGS)
                for sib in src.getParent().getChildren():
                    nm = sib.getName()
                    if nm == base or nm.startswith(prefixes):
                        sib.setVisibilityFlag(False)
            geo.setVisibilityFlag(True)
        geo.setPositions(p)
        geo.setIndices(i)
        geo.setNormals(n)
        line = stats_line(geo.getName(), stats, seconds)
        if values is not None:
            mode = s["analysis"][0]
            vr = self._value_range(mode, s["vrange"], stats)
            us = ramp_u(values, mode, vr)
            line += self._texture_result(geo, us, DEFECT_MATERIAL, RAMP_FILE,
                                         vrTextureTypes.RepeatMode.Clamp, 0.5)
            lo, mid, hi = legend_text(mode, vr)
            self.legend_lo.setText(lo)
            self.legend_mid.setText(mid)
            self.legend_hi.setText(hi)
            if mode == "deviation":
                line += ("\n    deviation %.3f .. %+.3f mm, 98%% within +/-%.3f mm; "
                         "colour range +/-%.3g mm"
                         % (stats["vmin"], stats["vmax"], stats["p98"], vr))
            else:
                tight = stats["vmax"]
                line += ("\n    curvature max %.3g /mm (radius %.3g mm); colour range %s"
                         % (tight, 1.0 / tight if tight > 0 else float("inf"), hi))
            line += "\n    " + ORIENTATIVE
            if s["label"]:
                self._add_note(geo, mode, vr, s["analysis"])
        if s["subdiv"]:
            vrGeometryService.subdivideGeometryPhong([geo], s["subdiv"])
        if switch is not None:
            self._show_in_switch(switch, geo)
            line += "\n    in switch %s (showing this version)" % switch.getName()
        self._say(line)

    def _part_switch(self, src):
        """The switch node holding this part's versions; created on first use. The
        original and any copies from earlier runs that sit next to it are moved in.
        A switch has no transform of its own, so nothing moves in the scene."""
        base = source_name(src.getName())
        parent = src.getParent()
        # startswith: VRED makes node names unique, so it may have become _versions1
        if parent.isType(vrdSwitchNode) and parent.getName().startswith(base + SWITCH_SUFFIX):
            return vrdSwitchNode(parent)
        switch = vrdSwitchNode(vrScenegraphService.createNode(
            vrScenegraphTypes.NodeType.SwitchNode, parent, base + SWITCH_SUFFIX))
        prefixes = tuple(base + tag for tag in RESULT_TAGS)
        members = [c for c in parent.getChildren()
                   if c.getName() == base or c.getName().startswith(prefixes)]
        if not any(c.getObjectId() == src.getObjectId() for c in members):
            members.insert(0, src)
        for c in members:
            switch.children.append(c)
            c.setVisibilityFlag(True)  # the switch decides what shows, not old hide flags
        self._say("Created switch %s with %d version(s)." % (switch.getName(), len(members)))
        return switch

    def _show_in_switch(self, switch, geo):
        for k, c in enumerate(switch.getChildren()):
            if c.getObjectId() == geo.getObjectId():
                switch.setChoice(k)
                return

    def _add_note(self, geo, mode, value_range, analysis):
        """VRED annotation on the map, so a screenshot carries the caveat with it."""
        if mode == "deviation":
            detail = ("local deviation, colour range approx. +/-%.3g mm, defect size %g mm"
                      % (value_range, analysis[1]))
        else:
            detail = "curvature, full red at radius approx. %.3g mm" % (1.0 / value_range)
        text = ("Defect map - ORIENTATIVE ONLY\n%s\nEstimated from the mesh geometry, "
                "not a CAE result." % detail)
        try:
            note = vrAnnotationService.createAnnotation(geo.getName() + "_note")
        except Exception as exc:
            self._say("Could not add the scene label: %s: %s" % (type(exc).__name__, exc))
            return
        self._call("annotation setText", note.setText, text)
        self._call("annotation setSceneNode", note.setSceneNode, geo)
        self._call("annotation setUseSceneNodeVisibility", note.setUseSceneNodeVisibility, True)
        try:
            bb = geo.getWorldBoundingBox()
            note.setPosition(bb.getMax())
        except Exception as exc:
            self._say("Could not place the scene label: %s: %s" % (type(exc).__name__, exc))

    @staticmethod
    def _value_range(mode, fixed, stats):
        if fixed > 0:
            return fixed if mode == "deviation" else 1.0 / fixed
        return stats["auto"] if stats["auto"] > 0 else 1e-6

    def _texture_result(self, geo, us, material_name, image_file, repeat, glow):
        """Write U coordinates (V = 0.5) to texture slot 0 and assign the texture material.
        Returns a log suffix describing what was applied."""
        uv = []
        for u in us:
            uv.append(u)
            uv.append(0.5)
        geo.setTexCoords(uv, 0, 2)
        mat = self._texture_material(material_name, image_file, repeat, glow)
        if mat is None:
            return "\n    WARNING no material applied - see the messages above"
        vrMaterialService.applyMaterialToNodes(mat, [geo])
        return "\n    material %s, %d texture coordinates" % (material_name, len(us))

    def _texture_material(self, name, image_file, repeat, glow):
        """A shared texture material, created on first use and reused by name. Its
        textures are (re)configured on every use, which also repairs a material left
        without an image by an earlier version.
        glow > 0 adds the texture as incandescence too, so colours read on unlit sides."""
        img = self._load_image(image_file)
        if img is None:
            return None
        mat = vrMaterialService.findMaterial(name)
        if mat is None or mat.isNull():
            try:
                mat = vrMaterialService.createMaterial(name,
                                                       vrMaterialTypes.MaterialType.Plastic)
            except Exception as exc:
                self._say("Could not create material %s: %s: %s"
                          % (name, type(exc).__name__, exc))
                return None
            self._say("Created material %s." % name)
        white = QtGui.QVector3D(1.0, 1.0, 1.0)
        self._call("setDiffuseColor", mat.setDiffuseColor, white)
        self._call("setGlossyColor", mat.setGlossyColor, QtGui.QVector3D(0.1, 0.1, 0.1))
        textures = [("diffuse", mat.getDiffuseTexture())]
        if glow > 0:
            try:
                inc = mat.getIncandescence()
                inc.setColor(white)
                inc.setIntensity(glow)
                textures.append(("incandescence", inc.getTexture()))
            except Exception as exc:
                self._say("Incandescence setup failed: %s: %s" % (type(exc).__name__, exc))
        for label, tex in textures:
            self._call(label + " setImage", tex.setImage, img)
            self._call(label + " setUseTexture", tex.setUseTexture, True)
            self._call(label + " setMappingType", tex.setMappingType,
                       vrTextureTypes.MappingType.UVMapping)
            self._call(label + " setRepeatModeU", tex.setRepeatModeU, repeat)
            self._call(label + " setRepeatModeV", tex.setRepeatModeV, repeat)
        try:
            got = textures[0][1].getImage()
            if got is None or got.isNull():
                self._say("WARNING %s: diffuse texture still has no image after setImage."
                          % name)
        except Exception as exc:
            self._say("Could not check the texture image: %s: %s" % (type(exc).__name__, exc))
        return mat

    def _load_image(self, filename):
        """Load a texture image shipped next to the plugin. VRED does not take an image
        built in memory (the texture stays empty), so it has to come from a file."""
        path = os.path.join(PLUGIN_DIR, filename)
        if not os.path.isfile(path):
            # file missing (incomplete install): write it from the built-in definition
            if not ramp_image().save(path):
                self._say("Texture file %s is missing and could not be written." % path)
                return None
            self._say("Wrote missing texture file %s." % path)
        try:
            img = vrImageService.loadImage(path)
        except Exception as exc:
            self._say("Could not load %s: %s: %s" % (path, type(exc).__name__, exc))
            return None
        if img is None or img.isNull():
            self._say("VRED could not load texture image %s." % path)
            return None
        return img

    def _cancel(self):
        # nothing is written until a part finishes, so a cancelled part leaves no trace
        name = self._job[0].getName() if self._job else None
        left = len(self._queue)
        self._job = None
        self._queue = []
        self._timer.stop()
        self._set_running(False)
        self._say("Cancelled%s; %d part(s) not processed."
                  % (" during " + name if name else "", left + (1 if name else 0)))

    def _finish(self):
        self._timer.stop()
        self._set_running(False)
        if self._settings["keep"]:
            self._say("Done. Originals kept%s." % (" (in switch)" if self._settings["switch"]
                                                   else " (hidden)"))
        else:
            self._say("Done. Replaced in place - not undoable.")


try:
    _host = VREDPluginWidget
except NameError:
    _host = None                       # running outside VRED (tests, syntax check)

if _host is not None:
    stlSmoothPanel = STLSmoothPanel(_host)
