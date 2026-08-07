r"""FpsLogger - average VR-session frame rate, split by context and render settings.

Menu: Scripts > FpsLogger   (tested against VRED 2027.1 / 19.1)

Community script. Not an Autodesk product: not developed, endorsed or supported
by Autodesk, and not covered by any Autodesk support entitlement. No warranty.

Install
    Copy the containing folder to, keeping the file name unchanged:
        <Documents>\Autodesk\VRED-<version>\ScriptPlugins\FpsLogger\vrFpsLogger.py
    VRED's Python sandbox must be disabled (Preferences > Script Settings) or no
    script plugin loads at all. That setting applies to every script VRED runs
    afterwards, not just this one. Restart VRED. See README.md for detail.

Workflow
    Press Start to arm. While armed, every HMD-active period (VR session, e.g.
    Innoactive / Apple Vision Pro over OpenXR) is captured automatically until Stop.

    The context column follows variant sets: executing a variant set named
    "Interior" or "Exterior" retags the capture, via the vrVariantService
    variantSetExecuted signal - no script inside the variant set is needed.
    A variant set may also call vredFpsSetContext("Interior") explicitly; the
    function is published into builtins so no import is required.

    A capture is closed and a new one opened whenever any of these change
    mid-session, so averages are never blended across settings:
        context, render engine, DLSS mode, raytraced reflections,
        real-time environment shadows mode

    Each finished capture with at least one sample appends a row to the panel
    table and to a tab-separated txt file next to the current scene. The
    hardware and VRED build are written into that file as a comment block the
    first time each armed run logs a row. Arming without ever entering VR
    writes nothing.

The live readout at the top of the panel shows what the plugin is reading right
now. If a value reads "n/a" there, it will be wrong in a session too - the
readout is the place to diagnose that, without putting the headset on.
"""
import os
import sys
import csv
import time
import ctypes
import platform
import builtins
from datetime import datetime

from PySide6 import QtCore, QtWidgets

# VRED injects v2 services (vrHMDService, vrVariantService, vrGPUService,
# vrRenderSettingsService, vrFileIOService) as bare names, but NOT the legacy v1
# modules - those must be imported by hand. Reading one without the import
# raises NameError, which is exactly how a frame rate silently becomes 0.0.
try:
    import vrOSGWidget
except ImportError:
    vrOSGWidget = None  # outside VRED - editor or unit test
try:
    import vrRenderSettings
except ImportError:
    vrRenderSettings = None
try:
    import vrController
except ImportError:
    vrController = None

try:
    _host = VREDPluginWidget  # noqa: F821
except NameError:
    _host = None

SAMPLE_INTERVAL_MS = 250

# Values accepted / returned by vrOSGWidget.get/setDLSSQuality, resolved off the
# module at runtime because the numeric values are not part of the public docs.
_DLSS_CONSTANTS = (
    ("VR_DLSS_OFF", "DLSS Off"),
    ("VR_DLSS_PERFORMANCE", "DLSS Performance"),
    ("VR_DLSS_BALANCED", "DLSS Balanced"),
    ("VR_DLSS_QUALITY", "DLSS Quality"),
    ("VR_DLSS_ULTRA_PERFORMANCE", "DLSS Ultra Performance"),
    ("VR_DLSS_DLAA", "DLAA"),
)

# Renderer selection, per the shipped examples/snippets/setRenderer script:
# rasterization mode 0/1 = OpenGL/Vulkan, raytracing mode 0/1 = CPU/GPU, with
# vrOSGWidget.getRaytracingEnabled() deciding which of the two pairs applies.
_RASTERIZATION_LABELS = {0: "OpenGL", 1: "Vulkan"}
_RAYTRACING_LABELS = {0: "CPU Raytracing", 1: "GPU Raytracing"}

# Real-time environment shadow modes. The Raytraced* entries are Vulkan-only.
_SHADOW_MODE_LABELS = (
    ("Off", "Off"),
    ("ScreenSpaceAmbientOcclusion", "SSAO"),
    ("RaytracedAmbientOcclusion", "Raytraced AO"),
    ("RaytracedEnvironmentShadows", "Raytraced Env Shadows"),
    ("RaytracedDiffuseGI", "Raytraced Diffuse GI"),
)

_reported = set()
_last_error = ""


def _report(where, exc):
    """Surface a failing VRED call once per call site instead of swallowing it."""
    global _last_error
    _last_error = "{}: {}: {}".format(where, type(exc).__name__, exc)
    if where not in _reported:
        _reported.add(where)
        print("[FpsLogger] " + _last_error)


def _safe(where, fn, default=None):
    try:
        return fn()
    except Exception as exc:
        _report(where, exc)
        return default


def _dlss_label_map():
    if vrOSGWidget is None:
        return {}
    labels = {}
    for const_name, pretty in _DLSS_CONSTANTS:
        value = getattr(vrOSGWidget, const_name, None)
        if value is not None:
            labels[value] = pretty
    return labels


def read_fps():
    """Current frame rate, or None if VRED will not report one."""
    if vrOSGWidget is None:
        return None
    try:
        return float(vrOSGWidget.getFPS())
    except Exception as exc:
        _report("getFPS", exc)
        return None


def read_engine():
    """(key, label) for the active renderer: OpenGL, Vulkan, CPU/GPU Raytracing."""
    if vrOSGWidget is None or vrRenderSettings is None:
        return None, "n/a"
    try:
        raytracing = bool(vrOSGWidget.getRaytracingEnabled())
    except Exception as exc:
        _report("getRaytracingEnabled", exc)
        return None, "n/a"
    if raytracing:
        mode = _safe("getRaytracingMode", vrRenderSettings.getRaytracingMode)
        return ("rt", mode), _RAYTRACING_LABELS.get(mode, "Raytracing mode {}".format(mode))
    mode = _safe("getRasterizationMode", vrRenderSettings.getRasterizationMode)
    return ("raster", mode), _RASTERIZATION_LABELS.get(mode, "Rasterization mode {}".format(mode))


def read_dlss():
    """(quality_value, label). quality_value is None when DLSS is unavailable."""
    if vrOSGWidget is None:
        return None, "n/a"
    try:
        if not vrOSGWidget.isDLSSSupported():
            return None, "DLSS Unsupported"
    except Exception as exc:
        _report("isDLSSSupported", exc)
        return None, "n/a"
    try:
        quality = vrOSGWidget.getDLSSQuality()
    except Exception as exc:
        _report("getDLSSQuality", exc)
        return None, "n/a"
    return quality, _dlss_label_map().get(quality, "DLSS mode {}".format(quality))


def _render_settings():
    return _safe("getSettings", lambda: vrRenderSettingsService.getSettings())  # noqa: F821


def read_raytraced_reflections(engine_key):
    """(value, label) for Vulkan raytraced reflections. Meaningless off Vulkan."""
    if engine_key != ("raster", 1):
        return None, "n/a"
    settings = _render_settings()
    if settings is None:
        return None, "n/a"
    value = _safe("getUseRaytracedReflections", settings.getUseRaytracedReflections)
    if value is None:
        return None, "n/a"
    return bool(value), "On" if value else "Off"


def read_shadow_mode(engine_key):
    """(value, label) for the real-time environment shadows mode.

    Reported for both rasterizers - SSAO exists in OpenGL - but the Raytraced*
    modes are Vulkan-only.
    """
    if engine_key is None or engine_key[0] != "raster":
        return None, "n/a"
    settings = _render_settings()
    if settings is None:
        return None, "n/a"
    mode = _safe("getRealtimeEnvironmentShadowsMode",
                 settings.getRealtimeEnvironmentShadowsMode)
    if mode is None:
        return None, "n/a"
    for attr_name, pretty in _SHADOW_MODE_LABELS:
        try:
            candidate = getattr(
                vrRenderSettingsTypes.RealtimeEnvironmentShadowsMode, attr_name)  # noqa: F821
        except Exception:
            continue
        if mode == candidate:
            return str(mode), pretty
    return str(mode), str(mode).rsplit(".", 1)[-1]


def read_hmd_active():
    """True while a VR display mode is running.

    Both services expose isHmdActive; which bare names VRED injects has varied,
    so try one then the other rather than betting on a single spelling.
    """
    try:
        return bool(vrHMDService.isHmdActive())  # noqa: F821
    except Exception as exc:
        first = exc
    try:
        return bool(vrImmersiveInteractionService.isHmdActive())  # noqa: F821
    except Exception:
        _report("isHmdActive", first)
        return False


def _total_ram_gb():
    """Physical RAM in GB via the Win32 API - no third-party dependency."""
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return round(status.ullTotalPhys / (1024 ** 3), 1)


def _join_version(parts):
    return ".".join(str(p) for p in parts) if parts else "n/a"


def system_info():
    """Hardware / build lines written into the log so results are attributable."""
    lines = []

    if vrController is not None:
        version = _safe("getVredVersion", vrController.getVredVersion, "n/a")
        year = _safe("getVredVersionYear", vrController.getVredVersionYear, "n/a")
        lines.append("VRED: {} ({})".format(version, year))

    lines.append("OS: {}".format(platform.platform()))
    lines.append("CPU: {} ({} logical cores)".format(
        platform.processor() or "unknown", os.cpu_count()))
    ram = _safe("GlobalMemoryStatusEx", _total_ram_gb)
    lines.append("RAM: {}".format("{} GB".format(ram) if ram else "n/a"))

    gpus = _safe("gpuInfo", lambda: vrGPUService.gpuInfo(), [])  # noqa: F821
    for index, gpu in enumerate(gpus or []):
        name = _safe("gpuInfo.getName", gpu.getName, "unknown")
        lines.append("GPU {}: {}".format(index, name))

    states = _safe("gpuStateInfo", lambda: vrGPUService.gpuStateInfo(), [])  # noqa: F821
    for index, state in enumerate(states or []):
        total = _safe("gpuStateInfo.getTotalMemory", state.getTotalMemory)
        if total is not None:
            lines.append("GPU {} memory: {:.0f} MB total".format(index, total))

    gl = _safe("openGLInfo", lambda: vrGPUService.openGLInfo())  # noqa: F821
    if gl is not None:
        lines.append("OpenGL: {} / {} (version {}, driver {})".format(
            _safe("getOpenGLVendor", gl.getOpenGLVendor, "n/a"),
            _safe("getOpenGLRenderer", gl.getOpenGLRenderer, "n/a"),
            _safe("getVersion", gl.getVersion, "n/a"),
            _join_version(_safe("gl.getDriverVersion", gl.getDriverVersion, []))))

    rt = _safe("raytracingInfo", lambda: vrGPUService.raytracingInfo())  # noqa: F821
    if rt is not None:
        lines.append("GPU raytracing supported: {} (driver {})".format(
            _safe("isGPURTSupported", rt.isGPURTSupported, "n/a"),
            _join_version(_safe("rt.getDriverVersion", rt.getDriverVersion, []))))

    runtime = _safe("getActiveOpenXRRuntimeName",
                    lambda: vrHMDService.getActiveOpenXRRuntimeName())  # noqa: F821
    system = _safe("getActiveOpenXRSystemName",
                   lambda: vrHMDService.getActiveOpenXRSystemName())  # noqa: F821
    if runtime or system:
        lines.append("OpenXR: {} / {}".format(runtime or "n/a", system or "n/a"))

    return lines


class _Accumulator:
    def __init__(self, context, signature, labels):
        self.context = context
        self.signature = signature   # compared to decide when to split a row
        self.labels = labels         # engine / dlss / reflections / shadows
        self._start = time.monotonic()
        self.sum_fps = 0.0
        self.count = 0
        self.min_fps = None
        self.max_fps = None

    def sample(self, fps):
        self.sum_fps += fps
        self.count += 1
        self.min_fps = fps if self.min_fps is None else min(self.min_fps, fps)
        self.max_fps = fps if self.max_fps is None else max(self.max_fps, fps)

    def finalize(self):
        duration = time.monotonic() - self._start
        avg = self.sum_fps / self.count if self.count else 0.0
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "context": self.context,
            "avg_fps": round(avg, 1),
            "min_fps": round(self.min_fps, 1) if self.min_fps is not None else 0.0,
            "max_fps": round(self.max_fps, 1) if self.max_fps is not None else 0.0,
            "duration_s": round(duration, 1),
            "samples": self.count,
        }
        row.update(self.labels)
        return row


_current_context = "Unknown"


def set_context(name):
    """Tag the active scenario. Also published as builtins.vredFpsSetContext."""
    global _current_context
    _current_context = str(name)
    if fpsLoggerPanel is not None:
        fpsLoggerPanel.on_context_changed(_current_context)


def read_state():
    """Everything that defines one log row, read in one pass."""
    engine_key, engine_label = read_engine()
    dlss_value, dlss_label = read_dlss()
    refl_value, refl_label = read_raytraced_reflections(engine_key)
    shadow_value, shadow_label = read_shadow_mode(engine_key)
    signature = (engine_key, dlss_value, refl_value, shadow_value)
    labels = {
        "engine": engine_label,
        "dlss": dlss_label,
        "reflections": refl_label,
        "shadows": shadow_label,
    }
    return signature, labels


class FpsLoggerPanel(QtWidgets.QWidget):
    COLUMNS = ["Timestamp", "Context", "Engine", "DLSS", "RT Reflections",
               "Env Shadows", "Avg FPS", "Min", "Max", "Duration (s)", "Samples"]
    _ROW_KEYS = ["timestamp", "context", "engine", "dlss", "reflections",
                 "shadows", "avg_fps", "min_fps", "max_fps", "duration_s", "samples"]

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is not None:
            layout = parent.layout() or QtWidgets.QVBoxLayout(parent)
            layout.addWidget(self)

        self._armed = False
        self._acc = None
        self._was_active = False
        self._pending_system_block = False

        self._build_ui()

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(SAMPLE_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()  # always on, so the live readout works before arming

        self._connect_variant_signal()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)

        row = QtWidgets.QHBoxLayout()
        self.startStopButton = QtWidgets.QPushButton("Start")
        self.startStopButton.clicked.connect(self._toggle_armed)
        self.statusLabel = QtWidgets.QLabel("Idle")
        row.addWidget(self.startStopButton)
        row.addWidget(self.statusLabel)
        row.addStretch()
        outer.addLayout(row)

        self.liveLabel = QtWidgets.QLabel("")
        self.liveLabel.setWordWrap(True)
        outer.addWidget(self.liveLabel)

        self.errorLabel = QtWidgets.QLabel("")
        self.errorLabel.setStyleSheet("color: #ff6666;")
        self.errorLabel.setWordWrap(True)
        self.errorLabel.setVisible(False)
        outer.addWidget(self.errorLabel)

        self.table = QtWidgets.QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        outer.addWidget(self.table)

        self.pathLabel = QtWidgets.QLabel("")
        self.pathLabel.setWordWrap(True)
        outer.addWidget(self.pathLabel)

        disclaimer = QtWidgets.QLabel(
            "Community script - not an Autodesk product, and not supported by Autodesk.")
        disclaimer.setStyleSheet("color: grey; font-size: 10px;")
        disclaimer.setWordWrap(True)
        outer.addWidget(disclaimer)

    def _connect_variant_signal(self):
        """Retag the context whenever a variant set is executed."""
        try:
            vrVariantService.variantSetExecuted.connect(self._on_variant_set_executed)  # noqa: F821
        except Exception as exc:
            _report("variantSetExecuted.connect", exc)

    def _on_variant_set_executed(self, variant_set_node):
        try:
            name = variant_set_node.getName()
        except Exception as exc:
            _report("variantSetNode.getName", exc)
            return
        set_context(name)

    def on_context_changed(self, name):
        if self._armed and self._acc is not None and self._acc.context != name:
            signature, labels = read_state()
            self._finalize_current(restart=(name, signature, labels))

    def _toggle_armed(self):
        if not self._armed:
            self._armed = True
            self._was_active = False
            self._acc = None
            self._pending_system_block = True
            self.startStopButton.setText("Stop")
            self.statusLabel.setText("Armed - waiting for VR session")
        else:
            self._armed = False
            if self._acc is not None:
                self._finalize_current()
            self.startStopButton.setText("Start")
            self.statusLabel.setText("Idle")

    def _tick(self):
        fps = read_fps()
        signature, labels = read_state()
        hmd_active = read_hmd_active()

        self.liveLabel.setText(
            "FPS: {}   |   {}   |   {}   |   RT Reflections: {}   |   "
            "Env Shadows: {}   |   Context: {}   |   HMD: {}".format(
                "n/a" if fps is None else "{:.1f}".format(fps),
                labels["engine"], labels["dlss"], labels["reflections"],
                labels["shadows"], _current_context,
                "active" if hmd_active else "off",
            )
        )
        if _last_error:
            self.errorLabel.setText(_last_error)
            self.errorLabel.setVisible(True)

        if not self._armed:
            return

        if hmd_active and not self._was_active:
            self._acc = _Accumulator(_current_context, signature, labels)
            self.statusLabel.setText("Capturing - {}".format(_current_context))

        elif hmd_active and self._acc is not None:
            if signature != self._acc.signature or _current_context != self._acc.context:
                self._finalize_current(restart=(_current_context, signature, labels))
            if fps is not None:
                self._acc.sample(fps)

        elif not hmd_active and self._was_active:
            if self._acc is not None:
                self._finalize_current()
            self.statusLabel.setText("Armed - waiting for VR session")

        self._was_active = hmd_active

    def _finalize_current(self, restart=None):
        if self._acc is not None and self._acc.count > 0:
            row = self._acc.finalize()
            self._append_row(row)
            self._write_log(row)
        self._acc = None
        if restart is not None:
            self._acc = _Accumulator(*restart)
            self.statusLabel.setText("Capturing - {}".format(restart[0]))

    def _append_row(self, row):
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, key in enumerate(self._ROW_KEYS):
            self.table.setItem(r, c, QtWidgets.QTableWidgetItem(str(row.get(key, ""))))
        self.table.scrollToBottom()

    def _log_file_path(self):
        scene_path = _safe("getFileName", lambda: vrFileIOService.getFileName(), "")  # noqa: F821
        if scene_path:
            return os.path.splitext(scene_path)[0] + "_fps_log.txt"
        return os.path.join(os.path.expanduser("~"), "vred_fps_log.txt")

    def _write_log(self, row):
        path = self._log_file_path()
        write_header = not os.path.exists(path)
        try:
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="\t")
                if self._pending_system_block:
                    self._pending_system_block = False
                    # CRLF throughout: csv.writer uses it, and a file with mixed
                    # endings renders badly in Notepad and Excel.
                    if not write_header:
                        f.write("\r\n")
                    f.write("# Session started {}\r\n".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    for line in system_info():
                        f.write("# {}\r\n".format(line))
                if write_header:
                    writer.writerow(self.COLUMNS)
                writer.writerow([row.get(key, "") for key in self._ROW_KEYS])
            self.pathLabel.setText("Log: " + path)
        except Exception as exc:
            _report("write log", exc)


fpsLoggerPanel = None

# Make set_context reachable from any VRED script scope (variant set Script
# fields, the Terminal) without an import, which script scopes cannot rely on.
builtins.vredFpsSetContext = set_context
if __name__ in sys.modules:
    sys.modules.setdefault("vrFpsLogger", sys.modules[__name__])

if _host is not None:
    fpsLoggerPanel = FpsLoggerPanel(_host)
