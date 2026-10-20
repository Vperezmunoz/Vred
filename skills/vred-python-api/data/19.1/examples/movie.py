# Movie player demo
# source: movie.html

# © 2026 Autodesk, Inc. All rights reserved.

screen = createPlane(2000, 1000, 1, 1, 0,0,0)
screen.setRotation(90,0,0)
screen.setTranslation(0, 0, 500)

mp = vrMoviePlayer2(screen.getMaterial(), "$VRED_EXAMPLES/video/demo.m1v")
mp.setLoop(true)
mp.setActive(true)
