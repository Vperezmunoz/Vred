# Manage Qt Quick applications for WebGL Streaming
# source: QtQuickStreaming.html

from PySide6 import QtCore, QtWidgets, QtGui, QtNetwork
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QFile, Signal, Slot, QObject, QProcess, QProcessEnvironment
from PySide6.QtNetwork import QTcpSocket

import os, signal
import uiTools

from vrController import vrLogError, vrLogWarning, vrLogInfo

"""
 This script plugin creates a convenience UI that lets you start and stop Qt Quick applications 
 with WebGL streaming enabled. Starting a process with this UI starts it as a child process of VRED.
 To work without the UI, you can use this command line:
 $ ./your-qt-application -platform webgl:port=8998
"""

# Load the .ui files. We derive widget classes from these types.
QtQuickStreaming_form, QtQuickStreaming_base = uiTools.loadUiType('QtQuickStreaming.ui')
ProcessWidget_form, ProcessWidget_base = uiTools.loadUiType('process.ui')


def getIcon(name):
    """Returns a QIcon for a button or action."""
    icon = QtGui.QIcon()
    iconPath = "resources:General/" + name
    icon.addPixmap(QtGui.QPixmap("{}Disabled.svg".format(iconPath)), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
    icon.addPixmap(QtGui.QPixmap("{}OffNormal.svg".format(iconPath)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


class RunningState:
    """ Indicates the state of the process."""
    STOPPED = 0
    STARTED = 1

    @staticmethod
    def createIndicatorPixmap(color):
        """Creates and returns a QPixmap with a circle as indicator for the process running state."""
        pixmap = QtGui.QPixmap(12, 12)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        painter.drawEllipse(1, 1, 10, 10)
        return pixmap


class ProcessObject(QObject):
    """ 
    Small wrapper around a QProcess object. 
    This class is responsible for starting and stopping a process and logging errors.
    Attributes:
        procName (str): Full application path
        port (int): Port for WebGL streaming
        process (QProcess): We use Qt to manage the process
        runningState (int): RunningState.STARTED or RunningState.STOPPED
    """
    runningStateChanged = Signal(int)
    def __init__(self, name, port):
        super(ProcessObject, self).__init__()
        self.procName = name
        self.port = port
        self.process = None
        self.runningState = RunningState.STOPPED

    def startProcess(self):
        if self.isRunning():
            return
        if not self.isPortAvailable(self.port):
            vrLogWarning("{}: Port {} already in use.".format(self.procName, str(self.port)))
        process = QProcess()
        self.process = process
        process.started.connect(self.processStarted)
        process.errorOccurred.connect(self.processError)
        process.finished.connect(self.processFinished)
        process.readyReadStandardError.connect(self.processStandardError)
        process.setWorkingDirectory(os.path.dirname(self.procName))
 
        # Enable WebGL platform for this process and set port via QT_QPA_PLATFORM environment 
        # variable. This is an alternative to using the -platform command line parameter.
        env = QProcessEnvironment.systemEnvironment()
        env.insert("QT_QPA_PLATFORM", "webgl:port={}".format(str(self.port)))
        process.setProcessEnvironment(env)
        process.start("\"{}\"".format(self.procName))

    def stopProcess(self):
        try:
            if self.isRunning():
                os.kill(self.process.processId(), signal.SIGTERM)
                self.process.waitForFinished(10000)
                self.process = None
        except:
            pass

    def isRunning(self):
        return (self.runningState == RunningState.STARTED and self.process is not None)

    def isPortAvailable(self, port):
        socket = QTcpSocket()
        free = socket.bind(port, QTcpSocket.DontShareAddress)
        socket.close()
        return free

    def processStarted(self):
        print("{} ({}): Process started.".format(self.procName, self.port))
        self.setRunningState(RunningState.STARTED)

    def processFinished(self, exitCode, exitStatus):
        print("{} ({}): Process finished.".format(self.procName, self.port))
        self.setRunningState(RunningState.STOPPED)

    def processError(self, err):
        if self.process is not None:
            vrLogError("{}: {}".format(self.procName, self.process.errorString()))

    def processStandardError(self):
        if self.process is not None:
            vrLogError("{}:\n{}".format(self.procName, self.process.readAllStandardError()))

    def getPath(self):
        return self.procName

    def getPort(self):
        return self.port

    def getRunningState(self):
        return self.runningState

    def setRunningState(self, state):
        self.runningState = state
        self.runningStateChanged.emit(state)


class ProcessWidget(ProcessWidget_form, ProcessWidget_base):
    """
    This widget holds the UI for one entry of the process list.
    Attributes:
        process (ProcessObject): The process represented by this widget
        id (int): Id of the widget to be able to find it in the list
    """
    deleteSignal = Signal(int)  
    id = 0
    def __init__(self, parent, process):
        super(ProcessWidget, self).__init__(parent)
        self.setupUi(self)
        self.process = process
        ProcessWidget.id += 1
        self.id = ProcessWidget.id

        self.startButton.clicked.connect(self._onStartButtonClicked)
        self.stopButton.clicked.connect(self._onStopButtonClicked)
        self.deleteButton.clicked.connect(self._onDeleteButtonClicked)
        self.copyURLButton.clicked.connect(self._onCopyURLButtonClicked)
        self.process.runningStateChanged.connect(self._onRunningStateChanged)

        self.startButton.setIcon(getIcon("Run"))
        self.stopButton.setIcon(getIcon("Stop"))
        self.deleteButton.setIcon(getIcon("Delete"))

        self.procLabel.setText(os.path.basename(self.process.procName))
        self.procLabel.setToolTip(self.process.procName)
        self.procLabel.setStatusTip(self.process.procName)
        self.portEdit.setValue(self.process.port)
        self.stoppedPixmap = RunningState.createIndicatorPixmap("#3c3c3c")
        self.startedPixmap = RunningState.createIndicatorPixmap("#41d971")
        self.updateUI()

    def updateUI(self):
        started = self.process.runningState == RunningState.STARTED
        self.startButton.setEnabled(not started)
        self.stopButton.setEnabled(started)
        self.portEdit.setReadOnly(started)
        runningPixmap = self.startedPixmap if started else self.stoppedPixmap
        self.runningLabel.setPixmap(runningPixmap)

    def _onStartButtonClicked(self):
        self.process.port = self.portEdit.value()
        self.process.startProcess()

    def _onStopButtonClicked(self):
        self.process.stopProcess()

    def _onDeleteButtonClicked(self):
        self.process.stopProcess()
        self.deleteSignal.emit(self.id)

    def _onCopyURLButtonClicked(self):
        url = "http://localhost:{}".format(self.process.port)
        QApplication.clipboard().setText(url)

    def _onRunningStateChanged(self, state):
        self.updateUI()


class QtQuickStreaming(QtQuickStreaming_form, QtQuickStreaming_base):
    """
    This is the main widget for the plugin. It holds a list of processes.
    Attributes:
        parent (QWidget): Parent widget
        processWidgets (dict of int:ProcessWidget): Holds all processes, maps id to process widget
        lastConfigFile (str): The config file that was loaded last
    """
    def __init__(self, parent=None):
        super(QtQuickStreaming, self).__init__(parent)
        parent.layout().addWidget(self)
        self.parent = parent
        self.setupUi(self)
        # This class derives from QMainWindow so that we can have a tool bar and a menu bar.
        # To be able to embed it into the parent widget provided by VRED we need to 
        # remove the Window flag.
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Window);
        self.processWidgets = {}
        self.lastConfigFile = ""

        # signal connections
        self.actionAdd.triggered.connect(self._onAdd)
        self.actionStartAll.triggered.connect(self._onStartAll)
        self.actionStopAll.triggered.connect(self._onStopAll)
        self.actionDeleteAll.triggered.connect(self._onDeleteAll)
        self.actionLoad.triggered.connect(self._onLoad)
        self.actionSave.triggered.connect(self._onSave)
        vrFileIOService.projectLoaded.connect(self._onProjectLoaded)

        # UI setup
        self.actionAdd.setIcon(getIcon("CreateNew"))
        self.actionStartAll.setIcon(getIcon("Run"))
        self.actionStopAll.setIcon(getIcon("Stop"))
        self.actionDeleteAll.setIcon(getIcon("Delete"))
        self.actionLoad.setIcon(getIcon("FileOpen"))
        self.actionSave.setIcon(getIcon("Save"))
        self.QuickActionBar.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu);
        self.updateUI();
        
    def _onAdd(self):
        exeFile = QFileDialog.getOpenFileName(None, "Select Executable", "", "*.exe")[0]
        if len(exeFile) > 0:
            port = self.getAvailablePort()
            self.addProcess(exeFile, port, self.autoStart.isChecked())

    def _onLoad(self):
        configFile = QFileDialog.getOpenFileName(None, "Load config file", "", "*.cfg")[0]
        if len(configFile) > 0:
            self.loadConfig(configFile)

    def _onSave(self):
        configFile = QFileDialog.getSaveFileName(None, "Save config file", self._getSuggestedFilename(), "*.cfg")[0]
        if len(configFile) > 0:
            self.saveConfig(configFile)

    def _getSuggestedFilename(self):
        # Suggest saving the config next to the current .vpb because it will be then 
        # automatically loaded with the vpb. See _onProjectLoaded.
        suggestedFilename = ".cfg"
        vredFile = vrFileIOService.getFileName()
        filepath, ext = os.path.splitext(vredFile)
        if ext == ".vpb":
            suggestedFilename = filepath + ".cfg"
        else:
            suggestedFilename = self.lastConfigFile
        return suggestedFilename

    def _onStartAll(self):
        for id in sorted(self.processWidgets):
            widget = self.processWidgets[id]
            widget.process.startProcess()

    def _onStopAll(self):
        for id in sorted(self.processWidgets):
            widget = self.processWidgets[id]
            widget.process.stopProcess()

    def _onDeleteAll(self):
        if len(self.processWidgets) == 0:
            return
        # Ask for confirmation before deleting everything.
        msgTitle = "QtQuickStreaming"
        msgText = "Stop and delete all processes from the list?\nThis cannot be undone."
        msgBox = QMessageBox(QMessageBox.Warning, msgTitle, msgText, QMessageBox.NoButton, self)
        deleteButton = msgBox.addButton("Delete", QMessageBox.ActionRole)
        cancelButton = msgBox.addButton(QMessageBox.Cancel)
        msgBox.exec_()
        if msgBox.clickedButton() == deleteButton:
            self.deleteAllProcesses()

    def _onProjectLoaded(self, file):
        """ Look for a .cfg file with the same name next to the loaded .vpb file and load it. """
        filepath, ext = os.path.splitext(file)
        if ext == ".vpb":
            configFile = filepath + ".cfg"
            if os.path.exists(configFile):
                print("Load config ", configFile)
                self.loadConfig(configFile)

    def _onProcessWidgetDeleted(self, id):
        procWidget = self.processWidgets.pop(id, None)
        self._deleteWidget(procWidget)
        self._onProcessListChanged()

    def _deleteWidget(self, procWidget):
        if procWidget is not None:
            procWidget.process.stopProcess()
            self.processWidgetsLayout.removeWidget(procWidget)
            procWidget.deleteLater()

    def deleteAllProcesses(self):
        for id, widget in list(self.processWidgets.items()):
            self._deleteWidget(widget)
        self.processWidgets = {}
        self._onProcessListChanged()

    def _onProcessListChanged(self):
        self.updateUI()

    def updateUI(self):
        hasProcesses = len(self.processWidgets) > 0
        self.actionSave.setEnabled(hasProcesses)
        self.actionStartAll.setEnabled(hasProcesses)
        self.actionStopAll.setEnabled(hasProcesses)
        self.actionDeleteAll.setEnabled(hasProcesses)

    def addProcess(self, name, port, doStart):
        # create process
        process = ProcessObject(name, port)
        if doStart:
            process.startProcess() 
        # create widget for process
        procWidget = ProcessWidget(self, process)
        procWidget.deleteSignal.connect(self._onProcessWidgetDeleted)
        self.processWidgets[procWidget.id] = procWidget
        self.processWidgetsLayout.addWidget(procWidget)
        self._onProcessListChanged()
        
    def getAvailablePort(self):
        """ Search for a port that is not used yet and return its number. """
        portRange = list(range(9000, 9100))
        socket = QTcpSocket()
        for p in portRange:
            if not self.isPortAssignedToProcess(p):
                free = socket.bind(p, QTcpSocket.DontShareAddress)
                socket.close()
                if free:
                    return p
        return 0

    def isPortAssignedToProcess(self, port):
        for id, widget in list(self.processWidgets.items()):
            if port == widget.process.getPort():
                return True
        return False

    def saveConfig(self, fileName):
        """ Write config file as a pipe delimited text file. """
        try:
            with open(fileName, 'w') as openedFile:
                for id in sorted(self.processWidgets):
                    widget = self.processWidgets[id]
                    path = widget.process.getPath()
                    port = widget.process.getPort()
                    running = int(widget.process.getRunningState())
                    openedFile.write("{}|{}|{}\n".format(path, port, running))
        except IOError as e:
            vrLogError("Could not save {0}. I/O error({1}): {2}".format(fileName, e.errno, e.strerror))
        except:
            vrLogError("Could not save {0}. Unexpected error.".format(fileName))

    def loadConfig(self, fileName):
        if os.path.exists(fileName):
            try:
                with open(fileName, 'r') as openedFile:
                    self.lastConfigFile = fileName
                    self.deleteAllProcesses()
                    for line in openedFile:
                        processName, port, runningState = line.strip().split('|')
                        if len(processName) > 0 and len(port) >0 and len(runningState) >0:
                            doStart = bool(runningState) and self.autoStart.isChecked()
                            self.addProcess(processName, int(port), doStart)
            except IOError as e:
                vrLogError("Could not load {0}. I/O error({1}): {2}".format(fileName, e.errno, e.strerror))
            except:
                vrLogError("Could not load {0}. Unexpected error.".format(fileName))


def onDestroyVREDScriptPlugin():
    """
    onDestroyVREDScriptPlugin() is called before this plugin is destroyed. 
    In this plugin we want to stop all processes.
    """
    streamingPlugin.deleteAllProcesses()


# Create the plugin widget
streamingPlugin = QtQuickStreaming(VREDPluginWidget)
