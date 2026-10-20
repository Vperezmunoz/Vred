# createMaterial
# source: createMaterial.html

# © 2026 Autodesk, Inc. All rights reserved.

# example for creating and editing a material with API v2

# create a plastic material
mat = vrMaterialService.createMaterial("My plastic material", vrMaterialTypes.Plastic)

# set the diffuse color to a beige tone. Colors need to be in linear space (gamma = 1)
mat.setDiffuseColor(QVector3D(0.79, 0.6, 0.328))

# set the roughness to 0.2 for a more shiny look. Values range from 0.0001 to 1.0
mat.setRoughness(0.2)

# load a texture and use it as diffuse map
examplesDir = vrFileIOService.getVREDExamplesDir()
diffuseImage = vrImageService.loadImage(examplesDir + "/textures/wood.png")
diffuseTex = mat.getDiffuseTexture()
diffuseTex.setImage(diffuseImage)
diffuseTex.setUseTexture(True)

# load a texture and use it as bump map
bumpImage = vrImageService.loadImage(examplesDir + "/textures/wood2.png", vrImageTypes.LoadType.Bump)
bumpTex = mat.getBumpTexture()
bumpTex.setImage(bumpImage)
bumpTex.setUseTexture(True)
bumpTex.setBumpIntensity(5.0)
