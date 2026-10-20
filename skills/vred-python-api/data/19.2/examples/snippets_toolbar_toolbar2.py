# A toolbar icon with a multiple actions in a submenu
# source: toolbar2.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example shows how to add a custom icon with a submeny to the VRED Toolbar.
# It creates a toolbar with multiple actions that open a URL in the default web browser.
# The actions are added to a drop-down menu that is displayed when the left mouse button is 
# held down on the toolbar icon.
# The toolbar is also added as a toggle to the View->Toolbars menu.

from PySide6 import QtGui, QtWidgets
import datetime, os
import webbrowser

def my_tool_action():
    print(f"My Tool: {datetime.datetime.now()}.")

def open_url_in_explorer(url):
    webbrowser.open(url)
    
def sub_menu_1():
    print('VRED Documentation...')
    open_url_in_explorer("https://help.autodesk.com/view/VREDPRODUCTS/2025/ENU/")

def sub_menu_2():
    print('Alias Documentation...')
    open_url_in_explorer("https://help.autodesk.com/view/ALIAS/2025/ENU/")

def sub_menu_3():
    print('Flow PT Documentation...')
    open_url_in_explorer("https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_user_wn_whats_new_html")

exampleFolder = os.path.join(os.getenv('VRED_ROOT'), "examples", "snippets", "toolbar")
iconPath = os.path.join(exampleFolder, "my_tool_icon.png")

my_action = QtGui.QAction(QIcon(iconPath), 'My Tool')
my_action.setToolTip('My Tool\n\nClick to activate.')

my_toolbar = QtWidgets.QToolBar('my_toolbar')
my_toolbar.setToolButtonStyle(QtGui.Qt.ToolButtonTextUnderIcon)
my_toolbar.addAction(my_action)

vrGUIService.addMainWindowToolBar(my_toolbar)

tool_action_1 = QtGui.QAction(my_toolbar.tr("VRED Help"))
tool_action_1.triggered.connect(sub_menu_1)

tool_action_2 = QtGui.QAction(my_toolbar.tr("Alias Help"))
tool_action_2.triggered.connect(sub_menu_2)

tool_action_3 = QtGui.QAction(my_toolbar.tr("Flow PT Help"))
tool_action_3.triggered.connect(sub_menu_3)

my_menu = QtWidgets.QMenu(my_toolbar.tr("My Menu"))
my_menu.addAction(tool_action_1)
my_menu.addAction(tool_action_2)
my_menu.addAction(tool_action_3)

my_action.setMenu(my_menu)
my_action.triggered.connect(my_tool_action)
