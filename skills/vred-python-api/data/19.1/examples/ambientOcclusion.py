# Simple ambient occlusion demo
# source: ambientOcclusion.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()
print("Executing simple ambient occlusion demo!")
print("Load a scene!")
loadGeometry("$VRED_EXAMPLES/geo/car.osb")
print("Update")
updateScene()


# define functions to call
def computeAO():
	print("Select the root node")
	selectNode("Speedshape")
	vrLogInfo("calculate ambient occlusion only")
	computeAmbientOcclusion(5, 0.05, 300.0, false, false, 0,0, false,0.1)

def computeAOSubdiv():
	print("Select the root node")
	selectNode("Speedshape")
	vrLogInfo("calculate ambient occlusion with subdivision")
	computeAmbientOcclusion(5, 0.05, 300.0, false, false, 0,0, true,0.1)

def computeIndirect():
	print("Select the root node")
	selectNode("Speedshape")
	vrLogInfo("calculate ambient occlusion with")
	vrLogInfo("2 bounces of indirect illumination")
	computeAmbientOcclusion(5, 0.05, 300.0, true, false, 4, 2, false,0.1)

def computeGI():
	print("Select the root node")
	selectNode("Speedshape")
	vrLogInfo("calculate ambient occlusion with 2 bounces of")
	vrLogInfo("indirect illumination, color bleeding and subdivision")
	computeAmbientOcclusion(5, 0.05, 300.0, true, true, 4,2, true, 0.1)
	
	
key1 = vrKey(Key_1)
key1.connect(computeAO)
vrLogInfo("Press key '1' to calculate ambient occlusion only")

key2 = vrKey(Key_2)
key2.connect(computeAOSubdiv)
vrLogInfo("Press key '2' to calculate ambient occlusion with subdivision")

key3 = vrKey(Key_3)
key3.connect(computeIndirect)
vrLogInfo("Press key '3' to calculate ambient occlusion with")
vrLogInfo("2 bounces of indirect illumination")

key4 = vrKey(Key_4)
key4.connect(computeGI)
vrLogInfo("Press key '4' to calculate ambient occlusion with 2 bounces of")
vrLogInfo("indirect illumination, color bleeding and subdivision")
