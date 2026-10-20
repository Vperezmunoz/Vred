# tagEditing
# source: tagEditing.html

# © 2026 Autodesk, Inc. All rights reserved.

# Changing node tags with API v2.

# add multiple tags to selected nodes. Note: only selected nodes are tagged, not their children.
selected = vrScenegraphService.getSelectedNodes()
vrMetadataService.addTags(selected, ["TagA", "TagB"])

# add a tag to materials
materials = [node.getMaterial() for node in selected if not node.getMaterial().isNull()]
vrMetadataService.addTags( materials, ["TagA"] )

# get all nodes with TagA
nodes = vrScenegraphService.getNodesWithAnyTag( ["TagA"])
print("Nodes with TagA:", len(nodes))
for n in nodes:
    print(n.getName())

# get all objects with TagA
objects = vrMetadataService.getObjectsWithTag( "TagA")
print("Objects with TagA:", len(objects))
for o in objects:
    # print(type(o))
    if o.isType(vrdNode):
        print("node:", vrdNode(o).getName())
    elif o.isType(vrdMaterial):
        print("material:", vrdMaterial(o).getName())


# check if a given node has a tag
print(vrMetadataService.hasTag( vrScenegraphService.getSelectedNode(), "TagB"))

# remove the tag from all nodes
vrMetadataService.removeTags( vrScenegraphService.getNodesWithAnyTag( ["TagA"]), ["TagA"])

# remove the tag from all objects
vrMetadataService.removeTags( vrMetadataService.getObjectsWithTag( "TagA"), ["TagA"])
