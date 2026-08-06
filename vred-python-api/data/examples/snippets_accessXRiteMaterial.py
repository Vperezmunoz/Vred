# accessXRiteMaterial
# source: accessXRiteMaterial.html

# © 2026 Autodesk, Inc. All rights reserved.

def getMeasuredMatFromXRite(xriteMat):
    childIndex = xriteMat.getChoice()
    children = xriteMat.getMaterials()
    if len(children) > childIndex:
        return children[childIndex]
    return vrdMaterial()

# load xrite material
mat = loadMaterialAssetByName("X-Rite Leather Suede Brown")
xriteMat = vrdXRiteMeasuredMaterial(vrdMaterial(mat))

# get its active measurement and modify its exposure
measuredMat = getMeasuredMatFromXRite(xriteMat)
measuredMat.setExposure(2.0)

# modify its color correction
colorCorrection = measuredMat.getColorCorrection()
colorCorrection.setHueShift(0.4)
colorCorrection.setSaturation(1.2)
colorCorrection.setContrast(0.8)
