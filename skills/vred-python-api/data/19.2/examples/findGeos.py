# Find geometry nodes
# source: findGeos.html

def findGeos(root):
    return vrNodeService.findNodes(lambda node: node.isType(vrdGeometryNode), vrdFindOptions(), root)

def isLineGeometry(node):
    return (node.isType(vrdGeometryNode)
        and node.getPrimitiveType() in (vrGeometryTypes.Lines, vrGeometryTypes.LineStrip))

def findLines(root):
    return vrNodeService.findNodes(isLineGeometry, vrdFindOptions(), root)

lines = findLines(vrScenegraphService.getRootNode())

def findBSides(root):
    predicate = lambda node: node.isType(vrdGeometryNode) and node.isBSide()
    return vrNodeService.findNodes(predicate, vrdFindOptions(), root)
