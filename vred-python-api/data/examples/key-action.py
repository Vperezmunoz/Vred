# Key events in the event loop
# source: key-action.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()

print("Executing test script!")

# Function parameter Test.

class TestAction(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
        print("vrAEBase Active = ", self.isActive())
    def msg(self):
        print("TestAction:msg ")
    def msg2(self, v):
        print("TestAction:msg2 ", v)

testaction = TestAction()

def doit():
    print("doit: Pressed key")

def doit1(key):
    print("doit1: Pressed key: ", key.getKey())

def doit2(value):
    print("doit2: Pressed key: ", value)

def doit3(value):
    print("doit3: Pressed key: ", value)

def doit4(value):
    print("doit4: Pressed key: ", value)

def doit5(key, value):
    print("doit5: Pressed key: ", key.getKey(), " value: ", value)

def doit6(key, key2):
    print("doit6: Pressed key: ", key.getKey(), " second time: ", key2.getKey())

keyAny = vrKey()

keyAny.connect(doit)
keyAny.connect("doit1(keyAny)")
keyAny.connect(doit1, keyAny)
keyAny.connect(doit2, 12)
keyAny.connect(doit3, "test")
keyAny.connect(doit4, 17.9)

# Now with two parameters. At the moment the maximum number of parameters is two.
keyAny.connect(doit5, keyAny, 42.11)
keyAny.connect(doit6, keyAny, keyAny)

# Calls method recEvent with integer parameter SWITCH_TOGGLE.
keyAny.connect(testaction, SWITCH_TOGGLE)

# Calls a class method 
keyAny.connect(testaction.msg)
# Calls a class method with parameter.
keyAny.connect(testaction.msg2, "vred")

print("End")
