# virtual eye example
# source: virtualeye.html

# © 2026 Autodesk, Inc. All rights reserved.

plane = createPlane(2000, 1000, 1, 1, 0,0,0)
plane.setRotation(-90,0,0)
plane.setTranslation(0, 0, 500)

sphere = createSphere(2, 250, 1,1,1)
sphere.setTranslation(-14, -1216, 471)

camera_beacon = createNode('Transform3D', 'camera_beacon')

ve = vrVirtualEye(plane.getMaterial(), camera_beacon, 256)
ve.setActive(true)
ct = ve.getCameraTransform()
ct.setTranslation(9, -29, 546)
ct.setRotation(-90, 0, 0)
ct.setScale(2, 1, 1)
