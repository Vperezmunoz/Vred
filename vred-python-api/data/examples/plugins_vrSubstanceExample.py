# Example UI for listing Substance materials
# source: vrSubstanceExample.html

# © 2026 Autodesk, Inc. All rights reserved.

# vrSubstanceExample shows a small UI for querying the substance materials
# in the scene  and registers it as an script plugin into VRED
from PySide6 import QtCore, QtGui, QtWidgets
import uiTools
from vrKernelServices import vrdSubstanceMaterial

# Create a form using the UI file created by QT Designer
vrSubstanceExample_form, vrSubstanceExample_base = uiTools.loadUiType('vrSubstanceExample.ui')

# We will use this class to generate python enumerations.
# For each query type we define a seperate value
class vrQueryType:
    Archive = 0
    Graph = 1
    Preset = 2

# This class implement all functionality from substance material query dialog
class vrSubstanceExample(vrSubstanceExample_form, vrSubstanceExample_base):
    # Constructor set connections between button and class methods
    # And add a resize grid an vottom rigth corner
    def __init__(self, parent=None):
        super(vrSubstanceExample, self).__init__(parent)
        parent.layout().addWidget(self)
        self.parent = parent
        self.setupUi(self)
        self.type = vrQueryType.Archive

        # add resize grip in bottom right corner.
        self.sizeGrip = QtWidgets.QSizeGrip(parent)
        self.sizeGrip.setFixedSize(16, 16)
        self.sizeGrip.move(parent.rect().bottomRight() - self.sizeGrip.rect().bottomRight())
        self.sizeGrip.raise_()
        self.sizeGrip.show()

        # connect signals with methods
        self.pbQuery.clicked.connect(self.makeQuery)
        self.rbArchive.clicked.connect(self.activateArchive)
        self.rbGraph.clicked.connect(self.activateGraph)
        self.rbPreset.clicked.connect(self.activatePreset)

    # Move resize grip to bottom right corner
    def resizeEvent(self, event):
        self.sizeGrip.move(self.parent.rect().bottomRight() - self.sizeGrip.rect().bottomRight())
        self.sizeGrip.raise_()

    # This method is called, when Query button was pressed
    def makeQuery(self):
        # Clean result table first
        self.tableWidget.clearContents()

        # Get all material and remove indvalid and non substance materials
        materials = vrMaterialService.getAllMaterials()
        valid = [item for item in materials if item.isValid()]
        substance = [item for item in valid if item.isType(vrdSubstanceMaterial)]

        # Look for the substance material name filter
        # If filter is set, look for all matching substance materials
        filter = self.leFilter.text()
        if not filter:
            filtered = substance
        else:
            filtered = [item for item in substance if filter in item.getName()]

        # Depending from type property we will call a method for a query
        # All results from will be shown in result table
        if self.type == vrQueryType.Archive:
            self.showArchive(filtered)

        if self.type == vrQueryType.Graph:
            self.showGraph(filtered)

        if self.type == vrQueryType.Preset:
            self.showPreset(filtered)

    # Shows for each item in a list of substance material the material name and all defined presets
    # Iterate over all material and all its presets
    # A substance material may contain one ore more presets
    # Substance materials with no presets will be suppressed
    def showPreset(self, materials):
        # Rename header column
        resultItem = QtWidgets.QTableWidgetItem("Presets")
        self.tableWidget.setHorizontalHeaderItem(1, resultItem)

        row = 0
        for material in materials:
            # Substance material name and a list of all its preset names
            name = material.getName()
            presets = material.getPresets()

            # Extend result table size
            count = len(presets)
            old = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(old + count)

            # Iterate over all presets and show name in the result table
            pos = 0
            for preset in presets:
                # Substance material name together the preset ID and preset name
                key = "{}({})".format(name, pos)
                itemName = QtWidgets.QTableWidgetItem(key)

                # Create the result table entries
                itemPreset = QtWidgets.QTableWidgetItem(preset.getName())
                self.tableWidget.setItem(row, 0, itemName)
                self.tableWidget.setItem(row, 1, itemPreset)
                row = row + 1
                pos = pos + 1

    # Shows for each item in a list of substance material the material name and the active graph
    # Iterate over all materials and query the active graph
    def showGraph(self, materials):
        # Rename header column
        resultItem = QtWidgets.QTableWidgetItem("Active Graph")
        self.tableWidget.setHorizontalHeaderItem(1, resultItem)

        # Set result table size
        count = len(materials)
        self.tableWidget.setRowCount(count)

        row = 0
        for material in materials:
            # Substance material namen and its active graph
            name = material.getName()
            graph = material.getActiveGraphName()

            # Create the result table entries
            itemName = QtWidgets.QTableWidgetItem(name)
            itemGraph = QtWidgets.QTableWidgetItem(graph)
            self.tableWidget.setItem(row, 0, itemName)
            self.tableWidget.setItem(row, 1, itemGraph)
            row = row + 1

    # Shows for each item in a list of substance material the material name and the full path of the substance archive
    # Iterate over all materials and query the archive path
    def showArchive(self, materials):
        # Rename header column
        resultItem = QtWidgets.QTableWidgetItem("Archive Path")
        self.tableWidget.setHorizontalHeaderItem(1, resultItem)

        # Set result table size
        count = len(materials)
        self.tableWidget.setRowCount(count)

        row = 0
        for material in materials:
            # Substance material name and the archive path
            name = material.getName()
            archive = material.getArchivePath()

            # Create the result table entries
            itemName = QtWidgets.QTableWidgetItem(name)
            itemArchive = QtWidgets.QTableWidgetItem(archive)
            self.tableWidget.setItem(row, 0, itemName)
            self.tableWidget.setItem(row, 1, itemArchive)
            row = row + 1

    # Handler called from 'Path' radio button set the type property
    def activateArchive(self):
        self.type = vrQueryType.Archive

    # Handler called from 'Graph' radio button set the type property
    def activateGraph(self):
        self.type = vrQueryType.Graph

    # Handler called from 'Preset' radio button set the type property
    def activatePreset(self):
        self.type = vrQueryType.Preset

# Create one instance from substance material query result form
substanceExample = vrSubstanceExample(VREDPluginWidget)
