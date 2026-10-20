# Create multiple snapshots
# source: snapshots.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()

import time, tempfile, os

number_of_snapshots = 5

path = os.path.join(tempfile.gettempdir(), 'vred_snapshots')
if not os.path.exists(path):    
    os.mkdir(path)
print("Using temp directory for snapshots: " + path)
# now delete all old snapshots.
for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
        if name[:4] == 'test':
            os.remove(os.path.join(root, name))
print("snapshot directory:", path)

box = createBox(1000, 1000, 1000, 10, 10, 10, 1.0, 0.0, 0.0)
updateScene()

#setSuperSampling(true)
setSnapshotQuality(75)

createSnapshotFastInit(640, 320)

t = time.time()
for i in range(number_of_snapshots):
    setCameraRotation(1.0 / number_of_snapshots, 0.0)
    filename = os.path.join(path, ('testa%04d.jpg') % (i))
    createSnapshotFast(filename)

box2 = createBox(1000, 1000, 1000, 10, 10, 10, 0.0, 0.0, 1.0)
box2.setTranslation(1000, 0, 0)
updateScene()
for i in range(number_of_snapshots):
    setCameraRotation(1.0 / number_of_snapshots, 0.0)
    filename = os.path.join(path, ('testb%04d.jpg') % (i))
    createSnapshotFast(filename)

createSnapshotFastTerminate()

sps = (1.0 / (time.time() - t)) * number_of_snapshots
print(sps, "snapshots per second.")
