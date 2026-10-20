# vrFade demo
# source: fade.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing fade script!")

newScene()

cloth = loadGeometry("$VRED_EXAMPLES/geo/cloth.osb")
car = loadGeometry("$VRED_EXAMPLES/geo/car.osb")
updateScene()

# fade object a single time from opaque to transparent and back in five seconds
fade = vrFade(car, 5.0)
fade.setActive(true)

# define timer object that toggles the fade object after 7 seconds. Because the duration
# of a single fade operation is 5 seconds, the fade object state is off, so the timer
# activates it back again
timer = vrTimer(7.0)
timer.connect(fade, SWITCH_TOGGLE)
timer.setActive(true)
