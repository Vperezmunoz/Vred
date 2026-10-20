# Connect two VRED instances (server script)
# source: ConnectionServer.html

# © 2026 Autodesk, Inc. All rights reserved.

# script to demonstrate how 2 vred instances can be linked together
# this is the script on the master
print("Executing connection script!")

# start master on port 1040
startVredServer(1040)

# load some geometry
newScene()
loadGeometry("$VRED_EXAMPLES/geo/cloth.osb")
loadGeometry("$VRED_EXAMPLES/geo/car.osb")
updateScene()
calcVertexNormals()
