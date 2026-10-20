# Interpolation demo
# source: interpolate.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing interpolate script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
loadGeometry("$VRED_EXAMPLES/geo/car.osb")
updateScene()
calcVertexNormals()

# find teddy and convert it into a transform node
teddy = findNode("Teddy_Bear");
teddy.makeTransform()

# create a interpolation object and add transformation slides to it
teddyDuration = 1.0
teddyInt = vrInterpolator()
teddySlide1 = vrTranslationSlide(teddy, 0,0,0, 100,0,0, teddyDuration)
teddySlide2 = vrRotationSlide(teddy, 0,0,0, 0,359,0, teddyDuration)
teddySlide3 = vrTranslationSlide(teddy, 100,0,0, 0,0,0, teddyDuration)
teddySlide4 = vrScaleSlide(teddy, 1,1,1, 2,2,2, teddyDuration)
teddySlide5 = vrScaleSlide(teddy, 2,2,2, 1,1,1, teddyDuration)

teddyInt.add(teddySlide1)
teddyInt.add(teddySlide2)
teddyInt.add(teddySlide3)
teddyInt.add(teddySlide2, true)
teddyInt.add(teddySlide4)
teddyInt.add(teddySlide5)
teddyInt.add(teddySlide2, true)
teddyInt.setActive(true);

# define key i to toggle interpolation on/off
keyI = vrKey(Key_I)
keyI.connect(teddyInt, SWITCH_TOGGLE)
print("press i to toggle interpolation of teddy")

# car
car = findNode("speedshape")
car.makeTransform()

# the "true" means when all slides are done it ends.
carInt = vrInterpolator(true)
carSlide1 = vrTranslationSlide(car, 0,0,0, 0,100,0, 8.0)
carSlide2 = vrTranslationSlide(car, 0,100,0, 0,0,0, 8.0)
carInt.add(carSlide1)
carInt.add(carSlide2)
carInt.setActive(true)

logo = findNode("chrome_logo")
logo.makeTransform()

logoInt = vrInterpolator(true)
logoSlide = vrRotationSlide(logo, 0,0,0, 0,359,0, 8.0)
logoInt.add(logoSlide)

# now connect the two actions, this could also be done in one interpolator,
# just shows the connection of actions.
# when the car interpolation is finished it will activate the logo interpolation
# when the logo interpolation is finished it will activate the car interpolation and so on ...
carInt.connect(logoInt, SWITCH_ON)
logoInt.connect(carInt, SWITCH_ON)

# tail
tail = findNode("Tail");
tail.makeTransform()

axis = createLine(0,0,0,0,0,1,0,0,0)
hideNode(axis)

tailInt = vrInterpolator()
tailSlide = vrRotationAxisSlide(tail, axis, 0, 359, 8.0)

tailInt.add(tailSlide)
tailInt.setActive(true)

print("End")
