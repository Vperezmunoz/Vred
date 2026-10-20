# Loading and repathing lightmaps
# source: lightmap.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collect all nodes with a valid base or separate lightmap in subtree   
def findNodesWithLightmapsRecursive(node, nodesWithLightmaps):
    if type(node) is vrdGeometryNode:   
        textureBake = node.getTextureBake()
        if textureBake.isValid():
            lightmap = textureBake.getLightmap()                  
            if lightmap.isValid():
                nodesWithLightmaps.append(node)
    for child in node.getChildren():
        findNodesWithLightmapsRecursive(child, nodesWithLightmaps)
        
# These example lines are based on the Toy_Excavator.vpb scene, you will need to adapt the
# node names and the folder to your scene.        
nodesWithLightmaps = []
findNodesWithLightmapsRecursive(vrNodeService.findNode("Toy_Excavator"), nodesWithLightmaps)

# Repathing to a folder with lightmaps for day scenario
vrBakeService.repathLightmaps(nodesWithLightmaps, getFileIOBaseDir() + "/BakingTextures_Day/")    

# Repathing to a folder with lightmaps for night scenario
vrBakeService.repathLightmaps(nodesWithLightmaps, getFileIOBaseDir() + "/BakingTextures_Night/")    

# © 2026 Autodesk, Inc. All rights reserved.

import re
import os

# Loading lightmaps from given path using the name of the specific node
def loadLightmapsByNodeName(nodesWithLightmaps, path):
    for node in nodesWithLightmaps:
        lightmapPaths = []
        # Create path to lightmap image
        baseLightmapPath = path + node.getName() + "_Lightmap" + ".exr"
        if os.path.isfile(baseLightmapPath):                    
            lightmapPaths.append(baseLightmapPath)    
            # Check if there is a corresponding separate lightmap, e.g.
            separateLightmapPath = path + node.getName() + "_SeparateLightmap" + ".exr"
            # The separate lightmap is optional. Only add the path if the file exists
            if os.path.isfile(separateLightmapPath):            
                lightmapPaths.append(separateLightmapPath)    
            # For this node load the given files
            vrBakeService.loadLightmaps([node], lightmapPaths)    
        else:
            print("Could not find base lightmap file:" + baseLightmapPath)

# Loading lightmaps from given path using the name of the specific lightmap.
# This can also be used if multiple nodes share the same name
def loadLightmapsByLightmapName(nodesWithLightmaps, path):
    for node in nodesWithLightmaps:
        lightmapPaths = []
        baseLightmap = node.getTextureBake().getBaseLightmap()
        # We can only use the lightmap name if we have a valid lightmap
        if baseLightmap.isValid():
            # Create path to lightmap image
            baseLightmapPath = path + baseLightmap.getName() + ".exr"
            if os.path.isfile(baseLightmapPath):                    
                lightmapPaths.append(baseLightmapPath)    
                # Check if there is a corresponding separate lightmap, same filename but with "_SeparateLightmap"
                separateLightmapPath = re.sub(r"_Lightmap([0-9]*)\.exr",r"_SeparateLightmap\1.exr",baseLightmapPath)
                # The separate lightmap is optional. Only add the path if the file exists
                if os.path.isfile(separateLightmapPath):            
                    lightmapPaths.append(separateLightmapPath)    
                # For this node load the given files
                vrBakeService.loadLightmaps([node], lightmapPaths)    
            else:
                print("Could not find base lightmap file:" + baseLightmapPath)


# These example lines are based on the Toy_Excavator.vpb scene, you will need to adapt the
# node names and the folder to your scene.

# Load by node name. Node names have to be unique.
loadLightmapsByLightmapName(vrNodeService.findNodes("Exhaust_Inner"), getFileIOBaseDir() + "/BakingTextures_Night/")

# Load by lightmap name Node names do not have to be unique, but lightmaps must be present
loadLightmapsByLightmapName(vrNodeService.findNodes("Exhaust_Inner"), getFileIOBaseDir() + "/BakingTextures_Day/")
