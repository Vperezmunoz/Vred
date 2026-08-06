# (Deprecated) countVisibleNodes
# source: countVisibleNodes.html

# © 2026 Autodesk, Inc. All rights reserved.

# Counts/collects visible geometry nodes with API v1.
# Note: This does not evaluate the choice of switch nodes.

nodelist = []
def countVisibleGeometry( node):
    if( node.getActive()):
        if( node.getType() == "Geometry"):
            nodelist.append(node)
        for i in range(0,node.getNChildren()):
            countVisibleGeometry( node.getChild(i))
        
def countVisibleGeometries( node):
    nodelist[:] = []
    countVisibleGeometry(node)
    print(len(nodelist))
