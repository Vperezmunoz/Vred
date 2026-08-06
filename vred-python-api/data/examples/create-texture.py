# Create texture and add it to a material
# source: create-texture.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example shows how to create a texture and add it to a material with API v2.
print("Executing create-texture script!")

# load a new scene
examplesDir = vrFileIOService.getVREDExamplesDir()
vrFileIOService.loadFile(examplesDir + "/geo/teddy.osb")

# load the image that we will use as texture
waterImage = vrImageService.loadImage(examplesDir + "/textures/Wasser1.png")

# find the material we want to change and edit its diffuse texture
furMaterial = vrMaterialService.findMaterials("fur_brown")[0]
furTexture = furMaterial.getDiffuseTexture()
furTexture.setImage(waterImage)
furTexture.setUseTexture(True)
