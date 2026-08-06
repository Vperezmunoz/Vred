# Load and export files
# source: import_export.html

# @@YEAR@@ Autodesk, Inc. All rights reserved.
#
# Example to show how to import and export files
#
# vrFileIOService is used to load a WRL file
# vrFileIOService is used to load a OSB file
# vrFileIOService is used to export nodes as FBX file as different FBX file versions
# vrdFileExportSettings is used to configure export settings
#

# Start with an empty scene
newScene()

# Import file names
theLogo = "/geo/alpha.wrl"
theTeddyBear = "/geo/teddy.osb"

# Node names of loaded files
theTeddyName = "Teddy_Bear"
theLogoName = "alpha"

# Export file template name
theExport = "/export{}.fbx"

# All FBX file version
theVersions = ["FBX-2020", "FBX-2019", "FBX-2018", "FBX-2016+2017", "FBX-2014+2015", "FBX-2013", "FBX-2012", "FBX-2011"]

# All FBX file version ids, same order as in theVersions
theVersionIDs = [0, 2019, 2018, 2016, 2014, 2013, 2012, 2011]

# Load a file from the examples
def loadFromExampleFolder(theName):
    theDir = vrFileIO.getVREDExamplesDir()
    theFile = theDir + theName
    return vrFileIOService.loadFile(theFile)


# Load the Teddy and the Logo example and add them to the scene
def loadExamples():
    # Import two files from example directory
    if not loadFromExampleFolder(theLogo):
        vrLogError("Can't load WRL file.")
        return False
    if not loadFromExampleFolder(theTeddyBear):
        vrLogError("Can't load OSB file.")
        return False
    return True


# Export a FBX file with different FBX file version to the VRED data directory
# We assume that the two files have already been loaded sucessfully
def exportFile(theName, theVersionID):
    global theTeddyName
    global theLogoName
    
    # Build the file path
    theDir = vrFileIO.getVREDDataDir()
    theFile = theDir + theName
    vrLogInfo("Save FBX file " + theFile)
    
    # Query the top level nodes from the two loaded files
    theTeddy = vrNodeService.findNode(theTeddyName)
    theLogo = vrNodeService.findNode(theLogoName)    
    theNodes = [ theTeddy, theLogo ]
    
    # First query the current export settings for this file type
    theSettings = vrFileIOService.getExportSettings(vrCADFileTypes.FileType.FBX)

    # Apply changes to the FBX settings
    theSettings.setExportEnvironmentGeometries(False)
    theSettings.setFbxVersionId(theVersionID)
    
    # After the export settings have been changed, you need to write the changed settings 
    # back to the file I/O service
    vrFileIOService.setExportSettings(vrCADFileTypes.FileType.FBX, theSettings)
    
    # Export all nodes from the two loaded files
    return vrFileIOService.exportNodes(theFile, theNodes)


# Now we load the two example files and then export them as different FBX format versions
if loadExamples():
    # Export as a FBX file with different FBX file version settings
    for i in range(len(theVersions)):
        theFile = theExport.format(theVersions[i])
        exportFile(theFile, theVersionIDs[i])
