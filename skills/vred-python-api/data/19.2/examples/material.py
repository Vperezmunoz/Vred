# Change existing material
# source: material.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example shows how to alter the diffuse and glossy color of a material with API v2.
print("Executing material script!")

# load a new scene
examplesDir = vrFileIOService.getVREDExamplesDir()
vrFileIOService.loadFile(examplesDir + "/geo/teddy.osb")

# find the material we want to change and edit its colors
furMaterial = vrMaterialService.findMaterials("fur_white")[0]
furMaterial.setDiffuseColor(QVector3D(0.3, 0.2, 0.5))
furMaterial.setGlossyColor(QVector3D(0.2, 0.1, 0.8))
