# Switch materials on keypress
# source: material-switch.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing material switch script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()

nose = findNode("Nose")

noseMat = nose.getMaterial()
white = findMaterial("fur_white")
brown = findMaterial("fur_brown")
black = findMaterial("plastic_black_glossy")

# define key 1 to switch to original material
key1 = vrKey(Key_1)
key1.connect("nose.setMaterial(noseMat)")
print("Press 1 to set material to original material")

# define key 2 to switch to white
key2 = vrKey(Key_2)
key2.connect("nose.setMaterial(white)")
print("Press 2 to set material to white")

# define key 3 to switch to brown
key3 = vrKey(Key_3)
key3.connect("nose.setMaterial(brown)")
print("Press F3 to set material to brown")

# define key 4 to switch to black
key4 = vrKey(Key_4)
key4.connect("nose.setMaterial(black)")
print("Press 4 to set material to black")

# define material list
materials = []
materials.append(noseMat)
materials.append(white)
materials.append(brown)
materials.append(black)

print(len(materials))

index = 0

# define function to switch to next/previous material
# parameter s is the increment
def setMaterials(s):
    global index

    index += s
    if index < 0:
        index = 0
    if index >= len(materials):
        index = len(materials) - 1
    nose.setMaterial(materials[index])


# define key + to switch to next material
keyPlus = vrKey(Key_Plus)
keyPlus.connect(setMaterials, 1)
print("Press + to switch to next material")

# define key - to switch to previous material
keyMinus = vrKey(Key_Minus)
keyMinus.connect(setMaterials, -1)
print("Press - to switch to previous material")
