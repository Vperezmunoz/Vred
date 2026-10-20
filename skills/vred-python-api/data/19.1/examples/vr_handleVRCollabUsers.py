# Reacting on joining and leaving users
# source: handleVRCollabUsers.html

# © 2026 Autodesk, Inc. All rights reserved.

def userArrived(user):
    print((user.getUserName() + " has arrived"))
    # create s sphere above the head of the new user
    color = user.getUserColor()
    sphere = createSphere(2, 200, color.redF(), color.greenF(), color.blueF())
    setTransformNodeTranslation(sphere,0,700,0,False)
    addChilds(user.getHeadNode(),[sphere])
    myName = vrSessionService.getUser().getUserName()
    hisName = user.getUserName()
    # send a greeting only to this user
    user.sendPython("print('Hi welcome {0} from {1}')".format(hisName,myName))

def userLeaves(user):
    print((user.getUserName() + " has left"))

vrSessionService.userArrives.connect(userArrived)
vrSessionService.userLeaves.connect(userLeaves)
