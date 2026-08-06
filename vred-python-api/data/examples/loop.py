# Insert code in the event loop
# source: loop.html

# © 2026 Autodesk, Inc. All rights reserved.

# example to show how to insert an object into the event loop
# the loop function of this object is called within each render frame
newScene()

#from random import *

print("Executing loop script!")

class TestAction(vrAEBase):
	def __init__(self):
		vrAEBase.__init__(self)
		self.addLoop()
	def recEvent(self, state):
		vrAEBase.recEvent(self, state)
		print("vrAEBase active = ", self.isActive())
	def loop(self):
		print("loop!")

ta = TestAction()
ta.setActive(true)

print("end")
