# Add and remove annotations
# source: annotations.html

# © 2026 Autodesk, Inc. All rights reserved.

import random

box1 = createBox(1000,1000,1000,10,10,10,1,1,0)
box1.setName("box1")

def addAnnotation():

    # create annotation
    annotation = vrAnnotationService.createAnnotation("annotation"); # identifier, made unique on creation
    # set text
    annotation.setText("Example description text\nwith 2 lines.");
    
    # change label size
    annotation.setSize(0.5)
    # random line color (border and arrow)
    r = random.random()
    g = random.random()
    b = random.random()
    lineColor = QColor();
    lineColor.setRgbF(r, g, b)
    annotation.setLineColor(lineColor)

    # change label opacity
    backgroundColor = annotation.getBackgroundColor()
    backgroundColor.setAlphaF(0.9) #change alpha
    annotation.setBackgroundColor(backgroundColor)

    # pick a position for the new annotation
    vrAnnotationService.pickAnnotation(annotation)

def deleteAllAnnotations():
    for annotation in vrAnnotationService.getAnnotations():
        vrAnnotationService.deleteAnnotation(annotation)
 

# Press "A" to add a new annotation
keyA = vrKey(Key_A)
keyA.connect(addAnnotation)

# Press "D" to delete all annotations
keyD = vrKey(Key_D)
keyD.connect(deleteAllAnnotations)
