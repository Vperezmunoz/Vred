# Open a dialog window with PySide
# source: pysideExampleDialog.html

# © 2026 Autodesk, Inc. All rights reserved.

from PySide6 import QtCore, QtWidgets

from shiboken6 import wrapInstance
def vredMainWindow() : 
    main_window_ptr = getMainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        boxlayout = QtWidgets.QVBoxLayout(self)

        self.lineedit = QtWidgets.QLineEdit()
        boxlayout.addWidget(self.lineedit)

        self.button = QtWidgets.QPushButton("Set Label")
        self.button.clicked.connect(self.buttonClicked)
        boxlayout.addWidget(self.button)

        self.label = QtWidgets.QLabel()
        boxlayout.addWidget(self.label)

        self.setLayout(boxlayout)

    def buttonClicked(self):
        self.label.setText(self.lineedit.text())
        self.lineedit.setText("")

if __name__ == "__main__":
    dialog = MyDialog(vredMainWindow())
    dialog.show()
