# Analog Clock example
# source: analog_clock.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing analog clock script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/analog_clock.osb")
updateScene()

from datetime import datetime
from PySide6.QtCore import QTimer
from PySide6.QtGui import QVector3D

# Deactivate clock: clock.stop()
# Reactivate clock: clock.start()
# Stop-Delete-Reset clock: clock.reset()


class clockWork():
    
    def __init__(self):
        self.needle_hours = vrNodeService.findNode("Clock_Needle_Hours")
        self.needle_minutes = vrNodeService.findNode("Clock_Needle_Minutes")
        self.needle_seconds = vrNodeService.findNode("Clock_Needle_Seconds")
        self.timer = QTimer();
        self.timer.timeout.connect(self.updateClock)
        
    def start(self):
        if self.timer.isActive():
            return
        self.timer.start()
        vrLogInfo('Clock activated')
    
    def stop(self):
        self.timer.stop()
        vrLogInfo('Stopping clock.')
    
    def reset(self):
        self.stop()
        self.needle_hours.setRotationAsEuler(QVector3D(0,0,0))
        self.needle_minutes.setRotationAsEuler(QVector3D(0,0,0))
        self.needle_seconds.setRotationAsEuler(QVector3D(0,0,0))
        vrLogInfo('Resetting clock.')
                        
    def getAngle(self, arg):
        return (arg / 60) * 360
    
    def getAngleHour(self, hour, minute):
        return (hour * 30) + (minute / 60) * 30
             
    def updateClock(self):
        now = datetime.now()
        
        seconds_angle = self.getAngle(now.second)
        minutes_angle = self.getAngle(now.minute)
        hours_angle = self.getAngleHour(now.hour, now.minute)
               
        self.needle_seconds.setRotationAsEuler(QVector3D(0, 0, -seconds_angle))
        self.needle_minutes.setRotationAsEuler(QVector3D(0, 0, -minutes_angle))
        self.needle_hours.setRotationAsEuler(QVector3D(0, 0, -hours_angle))
            
 
clock = clockWork()
clock.start()
