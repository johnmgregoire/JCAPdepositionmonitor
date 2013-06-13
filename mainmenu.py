# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 6/12/2013
# For JCAP

from PyQt4 import QtGui
from dictionary_helpers import getCol
from datareader import DATA_HEADINGS
import depositionwindow_data
import graphwindow_data
import profilewindow
import profilecreator
import os
import filename_handler
import process_deposition_data as pdd
import sys
import cPickle as pickle

DATA_FILE_DIR = 'C:/Users/JCAP-HTE/Documents/GitHub/JCAPdepositionmonitor'

""" window that pops up when application launches """
class MainMenu(QtGui.QWidget):

    def __init__(self):
        super(MainMenu, self).__init__()
        # holds all active windows
        self.graphWindows = []
        self.depWindows = []
        self.miscWindows = []
        # holds all profiles associated with current file
        self.profiles = {}
        # save name of file from which application will read
        self.file = self.initReader()
        filenameError = filename_handler.parseFilename(self.file)
        if filenameError:
            print 'ABORT'
            self.requestFileInfo(filenameError)
        # initialize data processor (includes reader)
        self.processor = pdd.ProcessorThread(parent=self, filename=self.file)
        self.processor.lineRead.connect(self.newLineRead)
        self.processor.newData.connect(self.depUpdate)
        self.processor.start()
                
        self.initUI()
        self.initSupplyVars()

    """ automatically loads last modified data file
        when application launches """
    def initReader(self):
        #targetDir = 'C:/Users/JCAP-HTE/Documents/GitHub/JCAPdepositionmonitor'
        lastModifiedFile = ''
        lastModifiedTime = 0
        # use os.walk() to recursively traverse directories if necessary
        allFiles = os.listdir(DATA_FILE_DIR)
        data = filter(lambda filename: filename.endswith('.csv'), allFiles)
        for filename in data:
            statbuf = os.stat(filename)
            if statbuf.st_mtime > lastModifiedTime:
                lastModifiedTime = statbuf.st_mtime
                lastModifiedFile = filename
        return lastModifiedFile

    """ draws graphical user interface """
    def initUI(self):
        self.setGeometry(50, 150, 300, 400)
        self.setWindowTitle('Deposition Monitor')
        self.layout = QtGui.QVBoxLayout(self)

        # load data file
        loadFileButton = QtGui.QPushButton('Choose Data File')
        self.layout.addWidget(loadFileButton)
        loadFileButton.clicked.connect(self.loadDataFile)

        # show single graph
        makeGraphButton = QtGui.QPushButton('Show Graph')
        self.layout.addWidget(makeGraphButton)
        makeGraphButton.clicked.connect(self.makeGraph)

        # create a profile
        makeProfileButton = QtGui.QPushButton('Create a New Profile')
        self.layout.addWidget(makeProfileButton)
        makeProfileButton.clicked.connect(self.makeProfile)

        # show a saved profile
        loadProfileButton = QtGui.QPushButton('Load a Saved Profile')
        self.layout.addWidget(loadProfileButton)
        loadProfileButton.clicked.connect(self.selectProfile)

        # show a deposition graph
        makeDepositionButton = QtGui.QPushButton('Create Deposition Graph')
        self.layout.addWidget(makeDepositionButton)
        makeDepositionButton.clicked.connect(self.makeDeposition)

        # end data collection session
        endButton = QtGui.QPushButton('End Experiment')
        self.layout.addWidget(endButton)
        endButton.clicked.connect(self.endExperiment)

        # initialize the timer that updates all graphs in application
        timer = pdd.QtCore.QTimer(self)
        timer.timeout.connect(self.redrawAll)
        # update graph every 1000 milliseconds
        timer.start(1000)

        self.show()

    """Initializes any variables that are useful for error checking"""
    def initSupplyVars(self):
        self.errors =[]
        self.supply = int(filename_handler.FILE_INFO.get("Supply"))
        
        if self.supply % 2 == 0:
            self.rfl = getCol("Power Supply" + str(self.supply) + " Rfl Power")
            self.fwd = getCol("Power Supply" + str(self.supply) + " Fwd Power")
            self.dcbias = getCol("Power Supply" + str(self.supply) + " DC Bias")

        if self.supply % 2 == 1:
            self.output_power = getCol("Power Supply" + str(self.supply) + \
                                       " Output Power")
            self.output_voltage = getCol("Power Supply" + str(self.supply) + \
                                         " Output Voltage")

    """ WORK IN PROGRESS """
    def requestFileInfo(self, tagsToEnter):
        dialog = QtGui.QDialog()
        dialog.setModal(True)
        labels = []
        lineEdits = []
        for tag in tagsToEnter:
            labels.append(QtGui.QLabel(tag+':', dialog))
            lineEdits.append(QtGui.QLineEdit(dialog))

    """ allows user to choose another data file """
    def loadDataFile(self):
        dirname = QtGui.QFileDialog.getOpenFileName(self, 'Open data file',
                                                      DATA_FILE_DIR,
                                                      'CSV files (*.csv)')
        # if cancel is clicked, dirname will be empty string
        if dirname != '':
            # converts Qstring to string
            dirString = str(dirname)
            # gets filename from current directory (will be changed eventually)
            dirList = dirString.split('/')
            self.file = dirList[len(dirList)-1]
            # hides all windows so they can be removed later
            for window in (self.graphWindows + self.depWindows + self.miscWindows):
                window.hide()
            # set everything up for the new file being read
            self.processor.newFile(self.file)
            self.initSupplyVars()

    """ creates window for single graph """
    def makeGraph(self):
        graph = graphwindow_data.GraphWindow(datafile=self.file)
        self.graphWindows.append(graph)
        graph.show()

    """ shows profile creator window """
    def makeProfile(self):
        profileCreator = profilecreator.ProfileCreator(datafile=self.file)
        self.miscWindows.append(profileCreator)
        profileCreator.show()

    """ shows load profile window """
    def selectProfile(self):
        savefile = open('saved_profiles.txt', 'rb')
        menuList = []
        savedProfiles = pickle.load(savefile)
        if not savedProfiles:
            error = QtGui.QMessageBox.information(None, "Load Profile Error",
                                                  "There are no saved profiles.")
            return
        # only show profiles with headings that correspond to this file
        for name, varsList in savedProfiles:
            if all(var in DATA_HEADINGS.values() for var in varsList):
                    self.profiles[name] = varsList
                    menuList += [name]
        savefile.close()
        loadMenu = profilewindow.LoadMenu(menuList)
        self.miscWindows.append(loadMenu)
        loadMenu.show()
        loadMenu.profileChosen.connect(self.loadProfile)
        loadMenu.profileToDelete.connect(self.deleteProfile)

    """ shows deposition graph window """
    def makeDeposition(self):
        depWindow = depositionwindow_data.DepositionWindow()
        self.depWindows.append(depWindow)

    """ once profile is chosen, loads profile in new window """
    def loadProfile(self, name):
        varsList = self.profiles.get(str(name))
        profileWindow = profilewindow.ProfileWindow(name, varsList)
        self.graphWindows.append(profileWindow)
        profileWindow.show()

    """ deletes a chosen profile from the LoadMenu """
    def deleteProfile(self, name):
        # savefile holds list of all profiles
        savefile = open('saved_profiles.txt', 'rb')
        savedProfiles = pickle.load(savefile)
        savefile.close()
        for profile in savedProfiles:
            if profile[0] == name:
                savedProfiles.remove(profile)
        # save updated list of profiles
        savefile = open('saved_profiles.txt', 'wb')
        pickle.dump(savedProfiles, savefile)
        savefile.close()

    """ sends new data received by reader to active graph windows """
    def updateGraphs(self, newRow):
        for window in self.graphWindows:
            window.updateWindow(newRow)

    """ sends new processed data to active deposition graph windows """
    def depUpdate(self, newDepRates):
        for window in self.depWindows:
            window.updateWindow(newDepRates)

    """ updates all active graph windows every second """
    def redrawAll(self):
        for windowType in (self.graphWindows,self.depWindows,self.miscWindows):
            for window in windowType:
                # release memory resources for all closed windows
                if window.isHidden():
                    windowType.remove(window)
                # graph windows will redraw; all other windows
                #   ignore this command
                else:
                    window.redrawWindow()
                    
    """ processes final data set and terminates reader at end of experiment """
    def endExperiment(self):
        self.processor.onEndExperiment()

    """ terminates reader (if still active) when main window is closed """
    def closeEvent(self, event):
        self.processor.end()
        event.accept()

    """ handles signal from reader when new line has been read """
    def newLineRead(self, newRow):
        self.updateGraphs(newRow)
        self.checkValidity(newRow)

    """ shows an error message if data indicates experiment failure"""
    def checkValidity(self, row):
        errors_list = []

        if self.supply % 2 == 0:
            fwdValue = float(row[self.fwd])
            dcBiasValue = float(row[self.dcbias])
            rflValue = float(row[self.rfl])
            
            if fwdValue < 5: errors_list.append("FWD power is below 5.")
            if dcBiasValue < 50: errors_list.append("DC bias is below 50.")
            if .10*fwdValue < rflValue:
                errors_list.append("RFL power is greater than 10% of FWD.")

        if self.supply % 2 == 1:
            opValue = float(row[self.output_power])
            if opValue < 5: errors_list.append("Output power is below 5") 

        newErrors = [ error for error in errors_list if error not in self.errors]
        self.errors += newErrors

        # only process error warning if no warning has been given to user
        if newErrors:
            message = "You have the following errors: " + " ".join(newErrors)
            validityError = QtGui.QMessageBox.information(None,"Unreliable Data Error", message)
        
""" main event loop """
def main():
    app = QtGui.QApplication(profilewindow.sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
