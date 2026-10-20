# selectLightVisibilityReference
# source: selectLightVisibilityReference.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get (and select) the visibility reference node of a light that's created on import of old scenes saved with VRED before 2017.

def selectLightVisibilityReferenceNode():
    selectedNode = getSelectedNode()
    if (selectedNode.isLight()):
        light = selectedNode.fields()
        reference = vrNodePtr(light.getFieldContainerID("visibilityReference"))
        selectNode(reference)

# Execute the function when key V is pressed in the render window.

KeyV = vrKey(Key_V)
KeyV.connect("selectLightVisibilityReferenceNode()")
KeyV.setDescription("Select legacy visibility reference node of selected light in scenegraph")
