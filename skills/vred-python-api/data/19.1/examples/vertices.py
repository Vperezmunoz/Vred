# vertex animation
# source: vertices.html

# © 2026 Autodesk, Inc. All rights reserved.

# animates some vertices of a simple cube.
newScene()

sign = 1.0

def animate(node):
    global sign
    positions = node.getPositions()
    new_positions = []
    for p in positions:
        p = p + 1 * sign
        new_positions.append(p)
    node.setPositions(new_positions)
    sign = sign * -1.0

node = createBox(0.5, 0.5, 0.5, 1, 1, 1,   1.0, 0.0, 0.0, 0)
# for vertices animation we disable the display list cache to get more speed!
node.setDlistCache(false)

timer = vrTimer(0.0)
timer.connect(animate, node)
timer.setActive(true)

updateScene()
setNear(0.1)
