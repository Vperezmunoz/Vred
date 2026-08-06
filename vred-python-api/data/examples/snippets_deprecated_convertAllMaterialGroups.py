# (Deprecated) convertAllMaterialGroups
# source: convertAllMaterialGroups.html

# © 2026 Autodesk, Inc. All rights reserved.

# Converts material group nodes to transform nodes with API v1.

nodelist = []
def convertMatGroup( node):
    if( node.getType() == "MaterialGroup"):
        nodelist.append(node)
    for i in range(0,node.getNChildren()):
        convertMatGroup( node.getChild(i))
    
def convertAllMatGroups( node):
    convertMatGroup(node)
    print(len(nodelist))
    for i in range(1, len(nodelist)):
        convertCore(nodelist[i], "Transform3D")
