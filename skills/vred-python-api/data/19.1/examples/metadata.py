# Metadata example
# source: metadata.html

# © 2026 Autodesk, Inc. All rights reserved.

# When importing CAD files in VRED version less than 2023.3 some meta data has been attached as a ValuePair.
# This function shows how to convert these ValuePair attachments in metadata sets.
def convertValuePairToObjectSet(node):
    # check if the node has a ValuePair attachement
    if node.hasAttachment('ValuePair'):
        attachment = node.getAttachment('ValuePair')
        keys = vrFieldAccess(attachment).getMString('key')
        values = vrFieldAccess(attachment).getMString('value')
        keyCount = len(keys)
        # a ValuePair attachement has two fields with string arrays
        # One is for keys one is for values
        # key[index] and value[index] gives one key/value pair in metadata
        if keyCount > 0 and len(values) == keyCount:
            # this gives access to all metadata sets attached to this node
            metadata = vrMetadataService.getMetadata(vrNodeService.getNodeFromId(node.getID()))
            # we do not create a new metadata set, we use nodes object set
            # object set is one metadata set for all key/value pairs attached directly to this node
            objectSet = metadata.getObjectSet()
            print("Add metadata entries from " + node.getName())
            # add all attached key value pairs to metadata object set
            for i in range(0, keyCount):
                objectSet.setValue(keys[i],values[i])
    # descend to all child nodes and look for a value pair attachement.
    for childIndex in range(0, node.getNChildren()):
        convertValuePairToObjectSet(node.getChild(childIndex))

# convert all nodes from scene. Start at the top node and descend to the lower nodes.
convertValuePairToObjectSet(getRootNode())
