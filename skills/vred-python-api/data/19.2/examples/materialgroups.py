# Material groups
# source: materialgroups.html

# Create the material
mat1 = vrMaterialService.createMaterial("plastic1", vrMaterialTypes.Plastic)

# Create the group (it will automatically get a unique name, but we rename it afterwards)
group1 = vrMaterialService.createMaterialGroup()
group1.setName("matgroup")

# Access the vrdMaterialNode that has been automatically created for the plastic material
mat1Node = vrMaterialService.findMaterialNode(mat1)

# Hierarchy modifications on vrdNodes are done by manipulating it's children class member
group1.children.append(mat1Node)

# Now the material will appear under the group. We can also move it back out to the top level
vrMaterialService.getMaterialRoot().children.append(mat1Node)
