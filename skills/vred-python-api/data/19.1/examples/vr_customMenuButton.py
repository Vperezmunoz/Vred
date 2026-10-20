# Adding buttons to the VR menu
# source: customMenuButton.html

# © 2026 Autodesk, Inc. All rights reserved.

from PySide6 import QtCore, QtGui, QtWidgets

icon1Base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHXSURBVFiF7ZaxaxRBFMa/t/vmvCN3HGclQohamCJoaxVshASblFZqLyKoIBgJucpChCjiHyB2QcFKIohRxErQSkVFk0BUEC7KyWZn9nbmWRhBMLc7ybEguL/2ffO9X7E7DFBS8r9DgxzWd4eO2FidEqN61qhOYNSNxtmVN4ULyCKqSVS95zRPOM0Qo+A0wxmOJQ4vti4tX/ftCrYjkPZ4GsDEJqMaiK6tzewfL0xAnmEEhAuZGWC6MIE0xSiAHZkhwuRSe0+1EAEiNDxidm97WRciIISOR6zr27dlATWOxwCeZ4aIbhYmsMEMgKTP7ON6N7rsW8Q+IZlvNTXsOWf4qNP8PX7Lq0FTT4W15AqAAxsxC8EtF4azw3NLsa9A7kWUPFCHrOH70LzTGYbTCqIZTnNXesGZ2si3pzauNBPNa63TX1Z8F3sJyCtUep/UC6d5TH7ddH8KwBmOkpT27Wp/+LrVxb/J/AZsBycAjPVP0BBbPr/d5bkCBOzOKyBQhuCAAg6o5zYIfhQmAMFCfoW8LkxAHcYjAE/6rgber0fR1cIEAMCG4UkQPfx7Qu/EBceH51a9//nN8HqQiIDiO/VjYtRBF1fqosOXjc7n29RGOsjykpKSf4KfPCOuDqfcAXQAAAAASUVORK5CYII="
icon2Base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD/SURBVFiF7ZS/SgNBEIe/3Tuw8U+pCAG1tvABFB/CwhcQX8W3ELzGMo9ga5EUgjZ2WmgaIcdxMdHbGYtbQpDz0EhsnA8Gdr/d4jezsGAYxn/HNcmjfXa2OhwQEggAHpF4GGDqJYnSR1+7p1xW1pd9MRwHsn5x0RYgbZLbHQ7PTv25Vg4qj04rmVnXxWcXPJe90eB4d22j9zB5yfpFBuhXAXzrfOZEFYavQjGRxgnP0jiB37K5mpYn3cHeeITQ0v3CAiylTq/uy5vv3F3IE/wEC2ABLEDjP5CXvF3f8qgiEBxaKYigAaQSNCT1vnIQ4p3gYznunt/zv27EMAzDmJsP9/R22LSjgbAAAAAASUVORK5CYII="

def hasClicked():
    print("click")    
def hasChecked():
    print("checked")    
def hasUnchecked():
    print("unchecked")
def submenuClosed():
    print("closed") 

# Push button function
tool1 = vrImmersiveUiService.createTool("CustomTool1")
tool1.setText("Tool 1")
tool1.setIconData(icon1Base64,"png")
tool1.signal().clicked.connect(hasClicked)

# Toggle button function, with on, off icon from file
icon = QtGui.QIcon()
icon.addFile("customMenuButtonOn.png",QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
icon.addFile("customMenuButtonOff.png",QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
tool2 = vrImmersiveUiService.createTool("CustomTool2")
tool2.setText("Tool 2")
tool2.setCheckable(True)
tool2.setIcon(icon)
tool2.signal().checked.connect(hasChecked)
tool2.signal().unchecked.connect(hasUnchecked)

# Open sub menu with web content
tool3 = vrImmersiveUiService.createTool("CustomTool3")
tool3.setText("Web GUI")
tool3.setIconData(icon2Base64,"png")
tool3.setViewContent('http://www.heise.de');
tool3.signal().viewClosed.connect(submenuClosed)

# Open sub menu with qt widget content
button = QtWidgets.QPushButton()
button.setText("Press me")
button.setFixedWidth(300)
button.setFixedHeight(200)
tool4 = vrImmersiveUiService.createTool("CustomTool4")
tool4.setText("Qt GUI")
tool4.setIconData(icon2Base64,"png")
tool4.setViewWidget(button);
tool4.signal().viewClosed.connect(submenuClosed)
