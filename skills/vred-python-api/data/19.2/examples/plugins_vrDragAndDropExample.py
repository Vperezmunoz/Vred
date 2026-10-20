# Example UI for accepting and decoding MIME data drops
# source: vrDragAndDropExample.html

from PySide6 import QtCore, QtGui, QtWidgets

import uiTools
from vrKernelServices import vrUserMimeTypes

vrDragAndDropExampleGUI_form, vrDragAndDropExampleGUI_base = uiTools.loadUiType('vrDragAndDropExampleGUI.ui')

class vrDragAndDropExample(vrDragAndDropExampleGUI_form, vrDragAndDropExampleGUI_base):
    def __init__(self, parent=None):
        super(vrDragAndDropExample, self).__init__(parent)
        parent.layout().addWidget(self)
        self.parent = parent
        self.setupUi(self)
        self.setMinimumSize(600, 400)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        mimeData = event.mimeData()

        droppedTypes = mimeData.formats()
        print(" \ndropped types: " + str(droppedTypes))

        # If you just want to decode a specific MIME type, you can just call:
        # - vrUserMimeTypes.decodeStrings (for string based types)
        # - vrUserMimeTypes.decodeObjects (for vrd object based types)
        # - vrUserMimeTypes.decode (for anything: strings, objects and custom types)
        # For example, use the following snippet to decode dropped nodes from the camera tree.
        # You can also omit the check if the mime data contains the specific MIME type. If the
        # data does not contain that type, the function will simply return an empty list.
        if vrUserMimeTypes.cameraTreeNode in droppedTypes:
            cameraTreeNodes = vrUserMimeTypes.decodeObjects(mimeData, vrUserMimeTypes.cameraTreeNode)

        # If you want to extract a specific data type and do not care about the MIME type,
        # you can search for a suitable MIME type using the findType function. For instance,
        # the following snippet finds the first suitable MIME type which contains vrd objects
        # and decodes them.
        objectType = vrUserMimeTypes.findType(droppedTypes, vrUserMimeTypes.DataType.VrdObject)
        objects = vrUserMimeTypes.decodeObjects(mimeData, objectType)

        # If you want all suitable MIME types instead of only one, use this snippet:
        objectTypes = vrUserMimeTypes.findTypes(droppedTypes, vrUserMimeTypes.DataType.VrdObject)
        for objectType in objectTypes:
            objects = vrUserMimeTypes.decodeObjects(mimeData, objectType)

        # If you want decode all supported types inside a drop, use this snippet:
        supportedTypes = vrUserMimeTypes.findTypes(droppedTypes, vrUserMimeTypes.DataType.Any)
        print("supported types in drop: " + str(supportedTypes))
        for supportedType in supportedTypes:
            decodedElements = vrUserMimeTypes.decode(mimeData, supportedType)
            print(supportedType + ": " + str(decodedElements))

instance = vrDragAndDropExample(VREDPluginWidget)
