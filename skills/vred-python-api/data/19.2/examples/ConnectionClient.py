# Connect two VRED instances (client script)
# source: ConnectionClient.html

# © 2026 Autodesk, Inc. All rights reserved.

# script to demonstrate how 2 vred instances can be linked together
# this is the script on the client
print("Executing connection script!")

# listen to master on localhost, port 1040
# server ip address or hostname and port number.
startVredClient("localhost", 1040)

# load some geometry
newScene()
loadGeometry("$VRED_EXAMPLES/geo/cloth.osb")
loadGeometry("$VRED_EXAMPLES/geo/car.osb")
updateScene()
calcVertexNormals()
