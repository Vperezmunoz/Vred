# Import own Python extensions
# source: import.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing import script!")

# This small example shows how to write your own python modules.
# The imported module is located in lib/myextension.py of the VRED Examples directory.
# In your own modules, you have to import VRED extension modules explicitly.
# For the main script, this is done by VRED automatically.

import os
import sys

# Add lib subdirectory of examples directory to module search path.
lib_dir = os.path.join(getVREDExamplesDir(), "lib")
if lib_dir not in sys.path:
    print(f"Adding: '{lib_dir}' to sys.path")
    sys.path.append(lib_dir)


import myextension

loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()
calcVertexNormals()

ext = myextension.MyExtension()
ext.init()

# © 2026 Autodesk, Inc. All rights reserved.

from vrScenegraph import *
from vrController import *
from vrKey import *

class MyExtension:
    def __init__(self):
        self.refs = []

    def init(self):
        print("MyExtension.init() called")
        print("Finding nodes 'Body' and 'Nose'")
        body = findNode("Body")
        nose = findNode("Nose")

        if body.isValid() and nose.isValid():
            print("Nodes found!")
        else:
            print("Nodes not found!")
            return
    
        print("Hiding 'Body' with key '1'")
        key1 = vrKey(Key_1)
        self.refs.append(key1)
        key1.connect(body.setActive, False)

        print("Hiding 'Nose'")
        nose.setActive(False)

        print("MyExtension.init() completed")
