# disableVertexCacheAnimation
# source: disableVertexCacheAnimation.html

# © 2026 Autodesk, Inc. All rights reserved.

def enableVertexCache( node, state):
    if node.hasAttachment("AnimAttachment"):
        animAttachment = node.getAttachment("AnimAttachment")
        animRootId = vrFieldAccess(animAttachment).getFieldContainerID("animationRoot")
        animRoot = vrNodePtr(animRootId)
        for childIdx in range(animRoot.getNChildren()):
            childNode = animRoot.getChild(childIdx)
            if childNode.getType() == "TimeShapeCache":
                childNode.setActive(state)
            
node = findNode("Tuch")
enableVertexCache(node, false)
