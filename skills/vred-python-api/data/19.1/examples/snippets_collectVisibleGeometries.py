# collectVisibleGeometries
# source: collectVisibleGeometries.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collects visible geometry nodes with API v2.

def collectVisibleGeometries( node):
    isVisibleGeo = lambda node: node.isType(vrdGeometryNode) and node.isVisible()
    nodelist = vrNodeService.findNodes( isVisibleGeo, vrdFindOptions(), node)
    print(len(nodelist))
    return nodelist
