# vrSpeech demo
# source: speech.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()

scene = loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()

# define speech input command show
speechShow = vrSpeech("show")
speechShow.connect(updateScene)
vrLogWarning("Say show to update the scene")

# define speech input command left
speechLeft = vrSpeech("left")
speechLeft.connect("setFrom(-1, -110.770012, 4.201654, 0.591690);setUp(-1, 0,1,0)")
vrLogWarning("Say left to look from the left")

# define speech input command right
speechRight = vrSpeech("right")
speechRight.connect("setFrom(-1, 110.256012, 11.424259, 1.052248);setUp(-1, 0,1,0)")
vrLogWarning("Say right to look from the right")

# define speech input command top
speechTop = vrSpeech("top")
speechTop.connect("setFrom(-1, 0.797391, 110.598511, 7.438207);setUp(-1, 0,0,-1)")
vrLogWarning("Say top to look from the top")

# define speech input command bottom
speechBottom = vrSpeech("bottom")
speechBottom.connect("setFrom(-1, 1.820974, -110.831238, 1.058094);setUp(-1, 0,0,1)")
vrLogWarning("Say bottom to look from the top")

# define speech input command name
speechName = vrSpeech("name")
speechName.connect("speak('My name is vreeed')")
vrLogWarning("Say name to hear the name of the application")

# rotation
scene.makeTransform()

sceneRotate = vrInterpolator()

# Das dreht einfach um die y-Achse also von winkel (0, 0, 0) bis (0, 359, 0) in 8 Sekunden
#drehtellerSlide = vrRotationSlide(drehteller, 0, 0, 0, 0, 359, 0, 8.0)

# Mann kann auch eine Achse angeben um die gedreht wird
# also (0.5, 0, 0.5) ist der erste Punkt der Achse und (0.5, 1, 0.5) der
# zweite Punkt der Achse und dann der winkel von 0 - 359.
rotateSlide = vrRotationAxisSlide(scene, 0.5, 0, 0.5,   0.5, 1, 0.5,  0, 359, 8.0)
sceneRotate.add(rotateSlide)

# define speech input command rotate
speechRotate = vrSpeech("rotate")
speechRotate.connect(sceneRotate, SWITCH_TOGGLE)
vrLogWarning("Say rotate to toggle rotation of the scene")

# define key r to rotate scene
keyR = vrKey(Key_R)
keyR.connect(sceneRotate, SWITCH_TOGGLE)
vrLogWarning("press key r to toggle rotation of the scene")

# wackel

sceneWiggle = vrInterpolator()

# turns around the y-axis (0-359 degrees) in 8 seconds
#drehtellerSlide = vrRotationSlide(drehteller, 0, 0, 0, 0, 359, 0, 8.0)

# You can also specify an axis to turn around
# (0.5, 0, 0.5) is the first point on the axis and (0.5, 1, 0.5) is
# the second point and later the start and stop angle
rotateSlide2 = vrRotationAxisSlide(scene, 0.5, 0, 0.5,   0.5, 1, 0.5,  0, 2, 0.5)
rotateSlide3 = vrRotationAxisSlide(scene, 0.5, 0, 0.5,   0.5, 1, 0.5,  2, 0, 0.5)
sceneWiggle.add(rotateSlide2)
sceneWiggle.add(rotateSlide3)

# define speech input command wiggle
speechWiggle = vrSpeech("wiggle")
speechWiggle.connect(sceneWiggle, SWITCH_TOGGLE)
vrLogWarning("Say wiggle to wiggle the scene")

# define key w to wiggle the scene
keyW = vrKey(Key_W)
keyW.connect(sceneWiggle, SWITCH_TOGGLE)
vrLogWarning("press key w to wiggle the scene")
