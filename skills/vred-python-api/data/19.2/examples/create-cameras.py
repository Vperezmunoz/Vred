# Create cameras
# source: create-cameras.html

# © 2026 Autodesk, Inc. All rights reserved.

# disable GUI updates
enableScenegraph(False)
try:

    # create a Perspective Camera, at the same position as the current active camera
    cameraName = "Perspective Camera"
    camera = vrCameraService.createCamera(cameraName)
    
    
    # create a Perspective Camera with aim constraint
    cameraName = "Perspective Aim Camera"
    aimName = "aim_1"
    camera = vrCameraService.createCamera(cameraName, 
                                          vrCameraTypes.ProjectionPerspective, 
                                          vrCameraTypes.ConstraintAim)
    aimNode = camera.getAimConstraintSources()[0]
    aimNode.setName(aimName)
    setTransformNodeTranslation(camera, 0,0,0, True)
    setTransformNodeTranslation(aimNode, 0,100,0, True)

    
    # create a Perspective Camera with aim and up vector constraint
    cameraName = "Perspective Aim+Up Camera"
    aimName = "aim_2"
    upName = "up_2"
    camera = vrCameraService.createCamera(cameraName, 
                                          vrCameraTypes.ProjectionPerspective, 
                                          vrCameraTypes.ConstraintAimUp)
    aimNode = camera.getAimConstraintSources()[0]
    aimNode.setName(aimName)    
    upNode = camera.getUpVectorConstraintSources()[0]
    upNode.setName(upName)
    setTransformNodeTranslation(camera, 0,0,0, True)
    setTransformNodeTranslation(aimNode, 0,100,0, True)
    setTransformNodeTranslation(upNode, 0,0,100, True)

finally:
    # reenable GUI updates
    enableScenegraph(True)
    updateScenegraph(True)
