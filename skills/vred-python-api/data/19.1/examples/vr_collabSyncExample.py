# Synchronization during a collaboration session
# source: collabSyncExample.html

# © 2026 Autodesk, Inc. All rights reserved.

testNode = None
loopCount = 1

def startTest():
    cmd = "node = createSphere(2,300,1,1,0);node.setName('test')"
    #send create command to all other users. This is always done asynchronously
    vrSessionService.sendPython(cmd,'testNodeState')
    
def stopTest():
    global testNode
    # create delete command and convert testNode to python string
    cmd = "deleteNode({})".format(vrSessionService.toPythonString(testNode))
    #send deletec command to all other users
    vrSessionService.sendPython(cmd,'testNodeState')

def testLoop():
    global timer, loopCount, testNode
    if loopCount == 1:
        # wait for the node to be created
        testNode = findNode('test')
        if not testNode.isValid():
            return
        # start synchronize the transformation
        vrSessionService.addNodeSync(testNode)
        vrSessionService.sendPython("print('sphere is moving')")
    if loopCount == 50:
        # stop synchronize the transformation
        vrSessionService.removeNodeSync(testNode)
        print('sphere only moves on this node')
    if loopCount == 75:
        # sync the current postion
        vrSessionService.syncNode(testNode)
    if loopCount == 100:
        stopTest()
        timer.setActive(False)
    # Animate object
    setTransformNodeTranslation(testNode, 0, 0, loopCount*10, True)
    loopCount+=1

timer = vrTimer(0.02)
timer.connect(testLoop)

def test():
    global loopCount
    loopCount = 1
    startTest()
    timer.setActive(True)

print("Enter test() to the console to start test")  
#test()
