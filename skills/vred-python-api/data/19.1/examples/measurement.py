# Measurement examples
# source: measurement.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()
hideNode(findNode("Environments"))
removeAllMeasurements()

#setup geometries

setTransformNodeTranslation(findNode("Perspective"), 9500,-10000,7000,True)

box1 = createBox(1000,1000,1000,10,10,10,1,1,0)
box1.setName("box1")
box2 = createBox(1000,1000,1000,10,10,10,1,0,0)
box2.setName("box2")
setTransformNodeTranslation(box2,4000,0,0,False) 

lineNode = createLine(0,0,0,4000,0,0,1,0,0)
lineNode.setName("Line")
group = createNode("Group", "Group", findNode("Root"))
group.addChild(box1)
group.addChild(lineNode)

cylinder1 = createCylinder(1000,500,20,True,True,True,0,0,1) 
cylinder1.setName("cylinder1")
setTransformNodeTranslation(cylinder1,2000,-4000,0,False) 

cylinder2 = createCylinder(1000,500,20,True,True,True,0,1,0) 
cylinder2.setName("cylinder2")
setTransformNodeTranslation(cylinder2,2000,0,-2000,False) 


# point to point measurement

p1 = Pnt3f(1792.9, -3500.0, 408.1)
p2 = Pnt3f(-305.0, -500.0, 419.0)
createPointPointMeasurement(cylinder1, p1, box1, p2)

# point to object measurement

p1 = Pnt3f(1923.3, -3500.0, -123.9)
createPointObjectMeasurement(cylinder1, p1, box2)

#object to object measurement

createObjectObjectMeasurement(cylinder1, box1)

# line to object measurement

p1 = Pnt3f(2000, 0, 0)
createLineObjectMeasurement(lineNode, p1, cylinder2)

# create circle measurement

p1 = Pnt3f(3580.0, -500.0, -455.5)
p2 = Pnt3f(2478.5, 6.9, -2135.8)
p3 = Pnt3f(4500.0, -10.8, -304.9)
createCircleMeasurement(box2,p1,cylinder2,p2,box2,p3)

# create gap measurement

p1 = Pnt3f(2083.9, -3500.0, -416.5)
p2 = Pnt3f(1868.1, -500.0, -2314.1)
createGapMeasurement(cylinder1, p1, cylinder2, p2)
