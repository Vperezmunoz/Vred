# Trigger touch sensors with the hands 2
# source: VR-hands-touchsensor-2.html

nodes = ["car", "button1", "button2", "button3"]

[setNodeInteractableInVR(findNode(name), True) for name in nodes]
