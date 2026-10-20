# substanceMaterialTools
# source: substanceMaterialTools.html

# © 2026 Autodesk, Inc. All rights reserved.

def refreshSubstanceMaterials(filter):
    materials = vrMaterialService.getAllMaterials()
    valid = [item for item in materials if item.isValid()]
    filtered = [item for item in valid if item.isType(vrKernelServices.vrdSubstanceMaterial)]
    found = [item for item in filtered if filter in item.getArchivePath()]
    for material in found:
        archive = material.getArchivePath()
        material.loadArchive(archive)

def refreshAllSubstanceMaterials():
    materials = vrMaterialService.getAllMaterials()
    valid = [item for item in materials if item.isValid()]
    found = [item for item in valid if item.isType(vrKernelServices.vrdSubstanceMaterial)]
    for material in found:
        archive = material.getArchivePath()
        material.loadArchive(archive)
