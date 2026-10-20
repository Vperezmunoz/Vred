# Query camera and tracking information
# source: showUserInfo.html

# © 2026 Autodesk, Inc. All rights reserved.

def showUserInfo(user):
    print((user.getUserName()))
    camPos = vrMathService.getTranslation(user.getCameraMatrix())
    camOri = vrMathService.getRotation(user.getCameraMatrix()).toEulerAngles()
    headTrackerPos = vrMathService.getTranslation(user.getHeadTrackingMatrix());
    print(("Camera Position: {0} {1} {2}".format(
        camPos.x(), camPos.y(), camPos.z())))
    print(("Camera Angles  : {0} {1} {2}".format(
        camOri.x(), camOri.y(), camOri.z())))
    print(("Head Tracker   : {0} {1} {2}".format(
        headTrackerPos.x(), headTrackerPos.y(), headTrackerPos.z())))
    headPos = vrMathService.getTranslation((user.getCameraMatrix() * user.getHeadTrackingMatrix()))
    print(("Head Position  : {0} {1} {2}".format(
        headPos.x(), headPos.y(), headPos.z())))
    if user.getHasLeftHand():
        print("Left hand tracked");
    if user.getHasRightHand():
        print("Right hand tracked");

def showAllUsers():
    for user in vrSessionService.getUsers():
        showUserInfo(user)

showAllUsers()
