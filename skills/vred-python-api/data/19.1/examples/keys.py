# Key input example
# source: keys.html

# © 2026 Autodesk, Inc. All rights reserved.

# Shows some multiple key allocation.

newScene()

print("Executing keys script!")

# define some functions that print some message when called
def key_a_0():
	print("Key A in keyboardlevel 0")

def key_b_0():
	print("Key B in keyboardlevel 0")

def key_a_1():
	print("Key A in keyboardlevel 1")

def key_b_1():
	print("Key B in keyboardlevel 1")

def key_a_2():
	print("Key A in keyboardlevel 2")

def key_b_2():
	print("Key B in keyboardlevel 2")

setDefaultKeyboardLevel(0);

keyA = vrKey(Key_A)
keyA.connect(key_a_0)

keyB = vrKey(Key_B)
keyB.connect(key_b_0)

# After this all created key events have a level of 1.
setDefaultKeyboardLevel(1);

keyA2 = vrKey(Key_A)
keyA2.connect(key_a_1)

keyB2 = vrKey(Key_B)
keyB2.connect(key_b_1)

# Ignore the default setting, first parameter is the keyboard level.
keyA3 = vrKey(2, Key_A, 0)
keyA3.connect(key_a_2)

keyB3 = vrKey(2, Key_B, 0)
keyB3.connect(key_b_2)

# reset keyboard level to default
setDefaultKeyboardLevel(-1);

# current keyboard level is 0
setKeyboardLevel(0)

# switch between keyboard levels.
key1 = vrKey(Key_1)
key1.connect("setKeyboardLevel(0)")
key1.connect("print 'switching to keyboard level 0'")
print("press 1 to toggle to keyboardlevel 0, keys A and B will get a different meaning")
key2 = vrKey(Key_2)
key2.connect("setKeyboardLevel(1)")
key2.connect("print 'switching to keyboard level 1'")
print("press 2 to toggle to keyboardlevel 1, keys A and B will get a different meaning")
key3 = vrKey(Key_3)
key3.connect("setKeyboardLevel(2)")
key3.connect("print 'switching to keyboard level 2'")
print("press 3 to toggle to keyboardlevel 2, keys A and B will get a different meaning")

print("End")
