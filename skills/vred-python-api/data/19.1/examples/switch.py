# vrSwitch example
# source: switch.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing switch script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
loadGeometry("$VRED_EXAMPLES/geo/cloth.osb")
updateScene()
calcVertexNormals()

# find geometry
nose = findNode("Nose")

# build switch object
switchNose = vrSwitch(nose)

#define key 1 to switch nose
key1 = vrKey(Key_1)
key1.connect(switchNose, SWITCH_TOGGLE)
vrLogInfo("Press key 1 to toggle nose")


# find geometry
teddy = findNode("Teddy_Bear")
cloth = findNode("Cloth_Example")

# build switch object
switch = vrSwitch([teddy, cloth])

#define key 2 to switch geometries
key2 = vrKey(Key_2)
key2.connect(switch, SWITCH_TOGGLE)
vrLogInfo("Press key 2 to toggle geometries")

print("End")
