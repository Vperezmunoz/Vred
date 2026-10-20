# convertAllMaterialGroups
# source: convertAllMaterialGroups.html

# © 2026 Autodesk, Inc. All rights reserved.

# Converts material group nodes to transform nodes with API v2.
    
def convertAllMatGroups( root):
    nodelist = vrNodeService.findNodes( lambda node: node.isType(vrdMaterialNode), vrdFindOptions(), root)
    print("found material groups:", len(nodelist))
    for n in nodelist:
        vrScenegraphService.convertNode(n, vrScenegraphTypes.TransformNode)
