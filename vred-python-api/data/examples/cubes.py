# Create cube demo
# source: cubes.html

# © 2026 Autodesk, Inc. All rights reserved.

# create a generic scene out of cubes with varying positions and colors
newScene()

setGradientBackground(-1, [Color3f(1.0, 0.0, 0.0), Color3f(0.0, 1.0, 0.0), Color3f(0.0, 0.0, 1.0)],
                    [1.0, 0.5 , 0.0])

# size
size = 2

# start color
rs = 0.0
gs = 0.0
bs = 0.0

# end color
re = 1.0
ge = 1.0
be = 1.0

x = - size
y = - size
z = - size

sr = (re - rs) / (size*2)
sg = (ge - gs) / (size*2)
sb = (be - bs) / (size*2)

r = rs
g = gs
b = bs

for i in range(size*2 * size*2 * size*2):
    node = createBox(0.5, 0.5, 0.5, 1, 1, 1, r, g, b, 0)
    node.makeTransform()
    node.setTranslation(x, y, z)
    x = x + 1
    r = r + sr
    if x == size:
        x = - size
        y = y + 1
        r = rs
        g = g + sg
        if y == size:
            y = - size
            z = z + 1
            g = gs
            b = b + sb

updateScene()

print("End")
