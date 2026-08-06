# vrTimer demo
# source: speed.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()

from random import *

print("Executing speed script!")

# vrAEBase Test	

n = 3
	
def end_msg():
	print("end")

ae_list = []
for i in range(n):
	ae = vrAEBase()
	ae_list.append(ae)
	
keyZ = vrKey(Key_Z)

keyZ.connect("print \"begin\"")
for i in range(n):
	keyZ.connect(ae_list[i], SWITCH_ON)
keyZ.connect(end_msg)

# vrTimer Test

def printIsActive(timer):
	print("Timer state: ", timer.isActive())
	
timer_list = []
for i in range(n):
	t = vrTimer(1)
	t.connect(printIsActive, t)
	t.setActive(true)
	timer_list.append(t)
	
keyT = vrKey(Key_T)
for i in range(n):
	keyT.connect(timer_list[i], SWITCH_TOGGLE)

print("End")
