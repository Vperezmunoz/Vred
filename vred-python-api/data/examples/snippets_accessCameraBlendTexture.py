# accessCameraBlendTexture
# source: accessCameraBlendTexture.html

# © 2026 Autodesk, Inc. All rights reserved.

# accessing camera blend image
selectNode('Perspective')
cam_node = getSelectedNode()
# get access to the tonemapping settings
toneMapAccess = vrFieldAccess(cam_node.fields().getFieldContainer('tonemappingSettings'))


# create a new image
leftEyeBlendImage = createImage()

#load the image
leftEyeBlendImage.read('C:/vred-snapshots/image.png')

# set the image
leftEyeBlendTexture = vrFieldAccess(toneMapAccess.getFieldContainer('leftEyeBlendingMap'))
leftEyeBlendTexture.setFieldContainerId('image', leftEyeBlendImage.getID())

# activate the blend texture
leftEyeBlendTexture.setBool('isActive',  1)

# set the blendmode
toneMapAccess.setUInt32('blendMode', 2)

#print the name
print(vrFieldAccess(leftEyeBlendTexture.getFieldContainer('image')).getString('name'))
