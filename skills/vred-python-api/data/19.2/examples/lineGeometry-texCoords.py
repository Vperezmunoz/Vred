# Create texture coordinates for line geometries
# source: lineGeometry-texCoords.html

# © 2026 Autodesk, Inc. All rights reserved.

""" This script creates UV coordinates for line geometries
    in the scene, so that a stipple pattern can be created 
    with a transparency texture.
    For demonstration purposes an example line geometry is 
    loaded.
"""

newScene()

class GeometryAccess(object):
    """ Helps accessing primitives and vertex data of a vrdGeometryNode.

        Args:
            geo (vrdGeometryNode): The geometry node. 
    """
    def __init__(self, geo):       
        if geo.isValid():
            self.__positions = geo.getPositions()
            self.__indices = geo.getIndices()
            self.__primType = geo.getPrimitiveType()
        else:
            self.__positions = []
            self.__indices = []
            self.__primType = None
                
    def isLineGeometry(self):
        """
            Returns: 
                Whether the geometry is a line geometry.
        """
        return GeometryAccess.isLine(self.__primType)
        
    def isLine(primType):
        """
            Returns: 
                Whether the type is a line primitive type.
        """
        return primType in (vrGeometryTypes.Lines, vrGeometryTypes.LineStrip)
        
        
    def getPosition(self, vertexIndex):
        """
            Args:
                vertexIndex (int): The vertex index in range from 0 to N-1
                                   where N is the vertex count.
            Returns: 
                3d vertex position.
        """    
        return QVector3D(self.__positions[3*vertexIndex], 
                         self.__positions[3*vertexIndex+1], 
                         self.__positions[3*vertexIndex+2])


    def getPrimitiveVertexIndices(self, primId):
        """
            Args:
                primId (int): The primitive index in range from 0 to N-1 
                              where N is the primitive count.
            Returns: 
                A list of vertex indices of a primitive: 3 indices for a 
                triangle, 2 for a line primitives, 1 for a point primitive.
        """
        if self.__primType == vrGeometryTypes.Points:
            v0 = primId
            return [self.__indices[v0]]
        elif self.__primType == vrGeometryTypes.Lines:
            v0 = primId * 2
            v1 = primId * 2 + 1
            return [self.__indices[v0], self.__indices[v1]]
        elif self.__primType == vrGeometryTypes.LineStrip:
            v0 = primId
            v1 = primId + 1
            return [self.__indices[v0], self.__indices[v1]]
        elif self.__primType == vrGeometryTypes.Triangles:
            v0 = primId * 3
            v1 = primId * 3 + 1
            v2 = primId * 3 + 2
            return [self.__indices[v0], self.__indices[v1], self.__indices[v2]]
        else:
            return []


def findLineGeos(root):
    """ Find line geometries in the scene tree. """
    predicate = lambda node : node.isType(vrdGeometryNode) and GeometryAccess.isLine(node.getPrimitiveType())
    lines = vrNodeService.findNodes(predicate, vrdFindOptions(), root)
    return lines


def createLineTexCoords(node):
    """Assigns texture coordinates (u, 0) to a given line geometry, with u 
       going from 0.0 (begin of line sequence) to "length" (end of line sequence).
       The coordinates along the line are calculated from the lengths of the 
       3D lines, and scaled such that the texture width corresponds to 100 mm 
       in the scene (world-scale texture coordinates)

    Args:
        node (vrdNode): A line geometry node. 
                        It is assumed that the geometry stores the lines
                        in the same order as they are concatenated in 3D. 
    """

    geo = vrdGeometryNode(node)
    geoAccess = GeometryAccess(geo)
    if not geoAccess.isLineGeometry():
        return
                    
    # Calculate lengths of all line segments, from start vertex
    # to each vertex along the line geometry.
    #
    # v0----v1----v2----v3
    # |
    # -------|
    # ------------|
    # -------------------|
    
    vertexCount = geo.getVertexCount()
    segmentLengths = [0.0] * vertexCount
    totalLength = 0.0

    # The world scale factor of the geometry is needed to 
    # calculate the actual world length of the lines.
    sx, sy, sz = toNode(geo.getObjectId()).getWorldScale()
    scale = QVector3D(sx, sy, sz)

    lineCount = geo.getPrimitiveCount()
    for lineId in range(0, lineCount):
        v0, v1 = geoAccess.getPrimitiveVertexIndices(lineId)
        p0 = geoAccess.getPosition(v0)
        p1 = geoAccess.getPosition(v1)
        lineLength = ((p1 - p0) * scale).length()
        segmentLengths[v0] = totalLength
        segmentLengths[v1] = totalLength + lineLength
        totalLength += lineLength

    # Create world-scale texture coordinates from list of lengths:

    # 1 in UV space corresponds to 100mm in scene units
    mmToUVUnit = 1.0 / 100.0
    # Pre-allocate flat list of 2d-coordinates for each vertex
    texCoords2f = [0.0] * (vertexCount * 2)     
    
    for i in range(0, vertexCount):
        u = segmentLengths[i] * mmToUVUnit
        texCoords2f[i * 2] = u
        # v-coordinate stays 0.0
        
    geo.setTexCoords(texCoords2f)


###########################################################

# Load example line geometry
loadGeometry("$VRED_EXAMPLES/geo/curve.osb")

# Find all line geometries in scenegraph
root = getRootNode()
lines = findLineGeos(root)
print ("Found line geometries:", len(lines))

# Create the texture coordinates
for line in lines:
    createLineTexCoords(line)
