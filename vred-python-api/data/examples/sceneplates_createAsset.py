# Create Asset
# source: createAsset.html

# © 2026 Autodesk, Inc. All rights reserved.

# Example to show how create sceneplate assets

# We introduce this types to make the code more readable
ContentType = vrSceneplateTypes.ContentType

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

theNode = vrSceneplateService.createNode(theRoot, vrSceneplateTypes.Frontplate, "Asset Test Frontplate")
thePlate = vrdSceneplateNode(theNode)
thePlate.setContentType(ContentType.Text)
thePlate.setText("Hello world")

# the name may be different form the name passed to create node (in case a sceneplate with this name already exists)
sceneplateName = str(thePlate.getName())

# this returns the currently selected sceneplate asset directory
# so, you have to make sure that 
directory = getSelectedAssetDirectory(VR_ASSET_SCENEPLATE)

if len(directory) == 0:
    print("ERROR: No sceneplate directory selected, open asset manager and select sceneplate directory.")
else:
    print(('Using directory:', directory))
    # this converts a decoupled vrdObject into a vrdNodePtr 
    sceneplateNode = vrNodePtr(thePlate.getObjectId())
    
    if not createSceneplateAsset(sceneplateNode, directory):
        print("ERROR: Unable to create sceneplate asset")
    else:
        print("Created sceneplate asset")
        # Load the stored asset again
        sceneplateNode2 = loadSceneplateAssetByName(sceneplateName)
        # And again by passing the directory
        sceneplateNode3 = loadSceneplateAssetByName(sceneplateName, directory)
        # Find the uuid of the asset and load the asset again
        attachment = sceneplateNode3.getAttachment("AssetAttachment")        
        uuid = vrFieldAccess(attachment).getString("uuid")       
        sceneplateNode4 = loadSceneplateAssetByUUID(uuid)
        # Overwriting one asset changes all assets
        thePlate.setText("HELLO WORLD!")
        overwriteSceneplateAsset(sceneplateNode)
