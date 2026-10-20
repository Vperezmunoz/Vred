# convertRoughness
# source: convertRoughness.html

# © 2026 Autodesk, Inc. All rights reserved.

# Functions for converting material roughness values between 2023 and 2024 mapping.

from math import sqrt, pow

def toNewRoughness(legacyRoughness):
    """ Converts legacy roughness value from VRED 2023 to new roughness value in 2024. """
    return sqrt(sqrt(legacyRoughness / 40.0))
    
def toLegacyRoughness(newRoughness):
    """ Converts new roughness value from VRED 2024 to legacy roughness value in 2023."""
    return pow(newRoughness, 4.0) * 40.0 


# Create a plastic material
mat = vrMaterialService.createMaterial("plastic material", vrMaterialTypes.Plastic)

# In VRED 2024, to set a legacy roughness value (e.g. 2.0) you need to convert it to the 2024 value
mat.setRoughness(toNewRoughness(2.0))
