# Gather all users in a collaboration session
# source: VRGatherUsersModule.html

from PySide6 import QtCore,QtWidgets
from vrOSGWidget import *

class GatherUsers():
    def __init__(self):
        QtCore.QTimer.singleShot(0, self.init)
    def init(self):
        self.createMenu()
    def createMenu(self):
        # png icons as base64 string
        icon = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAMAAAC5zwKfAAAAb1BMVEWtrrWmqKm1triwsbOur7GnqKqgoaOfoKKhoaS6u72ur7G5u72kpqikpaerq66tra+ipKa4ubutra6en6GztLadnqCgoaOlpaelpqimqKien6G8vL6qq624uLufn6Kqq624ubunp6qxsrSpqqy3ubs9lB+UAAAAJXRSTlMAJ//+/v37+EXvNy2FpWcakrwT3O3o/mDqYXrf0NzC7sRZ2+3dZjss4QAAAAlwSFlzAAAk6QAAJOkBUCTn+AAABGlJREFUWAntWNt2oyAURRE1RZMRMUmbzK0z//+Nszd4T0rU9GXWKg8Nctnsc+VQIba3KG6blDJJEqVUmmbb4bAz3/WIMeAc4lOA4sUDSql1XuRJuX+SoRCR4yilKPM8Kg/f0vQ5hkK8eKlFtd8XIldPM4QendTC5LUyJazyLENIbQFpapmoqP4MhuBopXxp4DUg+QkiQ0SdwA291xyf88NOX1q1gJ+iQ6JG0CDa8XgjsukOXf7rtuRKEfIG8BRHy5H8Sn0u2NGWFNNs6jZ7OMA6RBM1qfKIJDizsqHXW+1O3vvzP/xrTm4qYlJoHIn8DB3OrHyg1yuHmLljP8QTrzHn4NRKZZ6C0Ck4ztzGZbgdD4zTIOJbTEAuTzo86DFVMx36JTERrUoDUp+AJIQTqMlJ1Ted3biNO5RSQ5K6W3f7S2VjqZS7VuUD4s1iHptYeMExDLjDQim9wgeQvBn6XU9b3A+wWBoGlEgyN3jIFB3M6BeIzkkDgBeIgTaVdwQx6+ozAUM69IBL8E6xVdZFkVILGJ5tpgLOQKJ0CFiFmWMEuL9aW4/U04qM6/gRnhCMZ4QLAn0A5JhUycDlu1sEK8thbKa34fNUo4FQ/aMf+4n9ID2ccLX1pb5cLnUwnPr9844LSAktrMtEc5j+27j6oAd0CbWfXNkxWmN/B5jCLOYQbUc0FVQXF8LQBDCKNKZAJ662il4CR8VAvDpAGIV48JVtpnDEpIyTpi034hcDYNo73Sa1My4cEsbdM1/lQreAxzZHr7SIswVu8PQAW+Q5WBGQNzCts6GxrkLGU2lvgw5QbQM0FBDGVQMZSs4436ZD8YuAydim9CMoYQjK4awlvQMJtbeuX28cQ9vrYAnKeI2GA5aT3aZKknqjwLhTf8O8Zj/yEY4gw22zSQWBd2WJK6vxkWEKqqAqG/jm+lgxbQ6FEbCfVjA14Ng4MMqNYx0F+rCnb9x9ZKL/7b+Z9jm0luN7u90RVOk3I7oj/Mj4xgnwGqY8Ht2QfHi/dPeIG0nTOyXCsPtOr5ePgK6KoEXQ6Ng8Ylqq3kGYDhm3GaE8bPcj5AxE1KrrvNEnKhd5CVI1i7cBkPV51qwDFAdmaQdIAa/YfWBoY4QUY1WP3H0q3IdfUVHherZNXRbt5ui1er9wpCom8fghxP8ysYdMTV1fbCDrXb+/sxBpGkTQo4bCSCJPqyQUC5fOPrhjHzSUc97TgjW2B6TF5QPEU4x609JTFgBKLD0fF0jdFtlD9XYjlQ/DJSUxt/IZwGB9CNi+4m6Omw04fn98hplN9Z/UIarQO8+Kfknf0RYJJdM2+E75yyeFhfkeS433JZblogk+K3jdCK2QvB+VORHDn+8t5JOAQ6Cs2zllK3UOZgk+9Pz7qAk/b09xAiXhRZj0z+VeaaMO+bX/JIjfRuN3um/IkO1rOEN1dr8Zh+enH+AJ8eowSGFSrEyR+YxamekihFVA2W9r8aDHP8HYW3lRUMCVIk118vX1pYEvDXySBv4BiWoq9EUcJmMAAAAASUVORK5CYII="
        self.tool = vrImmersiveUiService.createTool("vrGatherUsersTools")
        self.tool.setGroup("Collaboration/Local User")
        self.tool.setText("Gather Users")
        self.tool.setIconData(icon)   
        self.tool.signal().clicked.connect(self.gatherUsers)
        self.tool.hideAway(True)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    def gatherUsers(self):
        vrSessionService.syncNode(vrCameraService.getActiveCamera())
        
gatherUsers = GatherUsers()

label = QtWidgets.QLabel(VREDPluginWidget)
label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
label.setScaledContents(True)
label.setText("Python VR gather users tool\n" + __file__)
VREDPluginWidget.layout().addWidget(label)
