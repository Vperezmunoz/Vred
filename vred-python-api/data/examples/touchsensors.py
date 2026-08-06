# Creating and deleting touch sensors
# source: touchsensors.html

# This example shows how to create touch sensors and
# connect them to a variant set.
# It also contains a function that deletes a touch sensor
# from a node.

def createTouchSensor(node):
    # Create the touch sensor first. This will create the needed
    # attachment and register the touch sensor in VRED.
    touchSensor = vrTouchSensor(node)

    # To add a variant set, that will be called whenever the touch
    # sensor is activated, we need to modify the attachement and
    # add the variant set directly.
    touchSensorAtt = node.getAttachment("TouchSensorAttachment")
    touchSensorAttAccess = vrFieldAccess(touchSensorAtt)

    # Note: this takes a list as parameter, so you can trigger multiple
    # variant sets
    touchSensorAttAccess.setMString("variantSets", ["toggleColor"])

    return touchSensor


def deleteTouchSensor(node):
  # To delete a touch sensor from a node, the touch sensor attachment
  # must be removed:
  if node.hasAttachment("TouchSensorAttachment"):
      att = node.getAttachment("TouchSensorAttachment")
      node.subAttachment(att)


tsensor1 = createTouchSensor(findNode("Cone"))
tsensor2 = createTouchSensor(findNode("Box"))

# Refresh the Touch Sensor UI
vrController.updateTouchSensors()
# Refresh the Scenegraph UI
vrScenegraph.updateScenegraph(False)
