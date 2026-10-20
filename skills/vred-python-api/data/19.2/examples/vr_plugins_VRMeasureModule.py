# Measure distances in VR
# source: VRMeasureModule.html

from PySide6 import QtCore,QtWidgets
from vrMeasurement import *
from vrOSGTypes import *

class Measure():
    def __init__(self):
        QtCore.QTimer.singleShot(0, self.init)
    def init(self):
        self.on = False
        self.point1Selected = False
        self.createMenu()
    def switchOn(self):
        if not self.on:
            self.point1Selected = False
            pointer = vrDeviceService.getInteraction("Pointer")
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.connect(self.selectPoint)
            self.on = True
    def switchOff(self):
        if self.on:
            pointer = vrDeviceService.getInteraction("Pointer")
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.disconnect(self.selectPoint)
            self.on = False
    def selectPoint(self,action,device):
        hit = device.pick()
        # ignore hitting the vr panel
        if not hit.hasHit() or hit.getNode().getName() == "VRMenuPanel":
            return
        if not self.point1Selected:
            self.point1Selected = True
            self.node1 = hit.getNode()
            self.point1 = hit.getPoint()
            self.removeMeasurement()
        else:
            self.point1Selected = False
            self.node2 = hit.getNode()
            self.point2 = hit.getPoint()
            self.createMeasurement()
    def createMenu(self):
        # png icons as base64 string
        onIcon = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAMAAAC5zwKfAAAAk1BMVEX5ohHvlxj5tgf1oxHylxjwjR7vhSLtfib4sQn6uwT3qw30nxTxjh7vhyLugyPvhyH4rwvvixzvhiLuhSLvhiHykxvwih/0oxHwjxzviCDtfSbwjx3tfyX6twX6uwT4sgj3qw31oRP5twbzmRf1ohL0nBX4sQn3qw3xlBnxkhvxjxzvhiH0nBX0nhTwjB7zmRf8wAGSQI6vAAAAMHRSTlMAIP///////kru/ycxUnKm9BCLOK4VUKNi5NVC6WDiu9Dt34NX9cFok8TU8eSz+nqRmIqRAAAACXBIWXMAACTpAAAk6QFQJOf4AAAEJUlEQVRYCe1YXWObOBDUp7nKgCsMLo2TkrSXpm56V/3/X9fZtXFCC5bA7Vv1YiSkYUa72l1ZiOVNhqCU0tyMMdauVlm2HA4r/3kDQOcI0QHvekAhgagBaNZ5URZ2U1zJEBzfgiEQfVVsfd3UVwOKXVBOOyfetUXlt/Z6QJEH7KDyALO+/h2AIjdA9O+1sc0NzJxqZe8nZ0og7m9h5eImnWHlzN0kYu70yQ3T/TAoc0HM2gBxnh8qdwlQ5FrbeScFgKtJyXiRwyY4KOmSlbMXAUW+gug5gDoCKOTcPYwBijyzUHzBdIMt+6DMzWBgpCMBlwy47e63IxjDIUYcDo32fLWpGiF80XXTx4VX5mkMa1jv1jcIfW8SEEc5DQYle0PRBgr4cvDq145MMEoF/8qyqgOgU9WvGMORfNgd62WcK6Rnhg9jM+aN5Yx3L8RHSnEhbusYfMVn9JMQ/6qgQohqjuGJ46FvvGhY82N0QWTCjgFrmvUZmp27UrOHYmhuCfCOATt6XN78IxjaFZ8Qj4yJFjktkW89EZ5lxULcc+ExnVsiWPx6Q3i2OLK6oz10m5R1U3M8557spNK/JckOgWJxe+L0eOb0hRiqp8VwQhyY4dlT9oEKo8NyQCim1PNiV64Gr9BcOgKk0ya1LfDTQbN27JWLaH6lbGu3YFgcc0rOm/i8CIxoUYWh39Py7sMxST1Q/WvkMkRfYq0xfNZODEkzEMtlgOKRbGIk2aQNR4ZrKi+NeTHTHGipiOCzWJ8BvfSPYGg0Dc1vFa011S64eteRUe61KSow1GqRZs93GtPIrnsu95DsP3atlCRZL9K8J37m9qisVfrr8emAclUbcqW5jcQZfXLiLuhTbdPyRpyPdzqq13SL649Zb2UhGnIcY+cz3DNeX3JB8unRH2gr7DlgJFP8wh7XnpjsTn6I5QVtrZ6t2UMvqPTKmm/PPSdPB3K+5iJgq/QpmQxl1ezwFHzmtP8C9tDtx5bsaQ9tv7tjM0bGPGIzIl+veDDDs2QrB4OxTsvBfmLnN2BoOODGYF7eH/im3tvhZZyftkpbGy/iX69qUFtqp0YVY97/ZOZZYbakUK8nS7eKU8OckIMCHV4zWd7m/B/IjNSyRlmklHm9CcNnunraVbqdv1OdFS5IKrmGujBh+H2P4heIFwhIvs3eThltCIfLL/8Fxenz51d9/4Yr7wm36iedfz+hDlSX8wZpXq0m3eAMxQ+oVNH60Dp81/dQmtD9PU3zFoBBfevXjv+y5ixN8zsCDJGKqGCGE4f9Jw6ObBIiajw5YuJ1m208Glpff7lOB4TeqGKkFr71vv7E5PNnAowoxmKyclrYfgJeN/m584varGzEcv1cAI4mk/798XcPo8R18NwyhOHa8V6WpUYH/5A0s0wlOM7n7+jfHfiDO/ADXuw2Qr3z2sAAAAAASUVORK5CYII="
        offIcon = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAMAAAC5zwKfAAAAb1BMVEWxsrWmp6m6vL21triwsbOur7GnqKqdnqGcnJyfoKK7u8Gpqayho6Sio6WoqKyurrG0tbevr7G3t7mfoKK1tritrrChoqWmp6m0tbijpKahpKSfoKKvsLO4ubyxsrS3uLisrK6pqqy2t7moqau3uLk51RP7AAAAJXRSTlMAQ+7//v7++zH+LYdkpxImvGeM4+jF1ObXw2J2Gt9ysJZXy9Z3MR72KQAAAAlwSFlzAAAk6QAAJOkBUCTn+AAAA9tJREFUWAntWNuC4iAMBaHUtrZSrc7NWeey//+NexKo1l0KVPdxeLEl4TQnCQkoxP1DrtQ4tC4MjbK8Hw4r11c8xXimegxwRNS6rmWzMa18FFCsmbXWopWya7dtVT1E+cpa2L7fCfkwZSG6LftRdHJvRGset1AIOWilur02pjssiHI375u1UXq9R5T7Yz5go1QzCymB6NKwyqYMR0XiVw8ajGlkp41SJgKI8JKJsG+BhVFAURvPOXenKFXEVevBMY5rXcMAysP1LfQkn8iFS3yY+jYhltmAgyr2Ibumc3VJJk5nIs/y8LyOiJ2oLjGSWlBomgYbpdtYG9kvBCSfsii/ICX2XUdFwNKyyJBlBuXaVPBN/8pVJcW7TnpaiB0lWNm8MaCNmMcimVIQgvJLVSdX997T+ikNCb5KAci1uG1KPyknxkpthPiVxzkJiGxFusKwEwOq5IKEAhgD74W03hkxw+tRyBaAKO6k4xLHRtXTQsYzvEM4tdGP0osiGhsGbJ3GgTmztZElcdGZAT2GfDzOXcGVfWTp4jy+xU0JS3vG+xiFlhE/x9c7fg8MKMeVjvNhfF3+C8ZAnDSTR7dfr8hCijGaGkXmTJy1j9FyA8VRkYXEGNDE1HHOqHnhj5008Apm3Ct9JKWBLNR1WD85u2MXWtLDtmNAHJoAOH9uimMOACwMm7PzgCizWus7OdfwYIEYU031FsruqIGo7uMMerh+NGulrdyQhUdtep5UH3FqM9IVsdPbemefrV2tjt37od9uaU6bmSXRaQlyRcGhEIItZPUjf+ayeaIQt8IWjIvCJzGaqIdGAsFCX9BuV8TffDk9Oa2rhTSPUC0vOe4e9+W/OuYhXlFmYeJyzpYLwacH7C+URU+U9XLOaMYYI7Pue7jYVHCcR4n/YvLnk/FsSM/CQt8IQ+KZuS8GvFg11ZIALMx5OpV+9jEOKnZ0fS/MslMO8g7DBgFFSxa65h9WCMw6xjPHS5RZOHFRa3GMV4Ev8dTAYVnC+XeMMR1qqdcsKbOc1GqGMVoL3z395p6jMZ3n46+etM+pkJ73sLBytfxvUfDdnRB2QRlPNmC8hLM7WkbqPN1mK5PN2R1+o+pHGFhll5wkY9zWCK/KLTmcM5dCE/TklnxYZbZTd96IMkaZJRMzOTvGr0HLLpM9mZiZ23R+uZbWC8TtQ0d7pczjzHhjM7mFmbzhvpH7DwMDjs1kAnH7SJyzrttCfBNiumWU+NcnETlvAt2Y7K05oTeUWfUWEvw7h50XbCa3mrIwGTx4zZmux+kx0KU3b6xsjt5ulXZ0Ds6Pzo8H/r8H/gCZDSF/0DUijwAAAABJRU5ErkJggg=="
        self.tool = vrImmersiveUiService.createTool("vrMeasureTool")
        self.tool.setText("Measure")
        self.tool.setCheckable(True)
        self.tool.setOnOffIconData(onIcon,offIcon)   
        self.tool.signal().checked.connect(self.switchOn)
        self.tool.signal().unchecked.connect(self.switchOff)
        self.tool.hideAway(True)
    def createMeasurement(self):
        vrSessionService.sendPython("createPointPointMeasurement({},{},{},{})".format(
            vrSessionService.toPythonString(self.node1),
            vrSessionService.toPythonString(self.point1),
            vrSessionService.toPythonString(self.node2),
            vrSessionService.toPythonString(self.point2)))
        #createPointPointMeasurement(self.node1,self.point1,self.node2,self.point2)
    def removeMeasurement(self):
        vrSessionService.sendPython("removeSelectedMeasurement()")
        
measure = Measure()

label = QtWidgets.QLabel(VREDPluginWidget)
label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
label.setScaledContents(True)
label.setText("Python VR measurement tool\n" + __file__)
VREDPluginWidget.layout().addWidget(label)
