# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 6/13/2013
# For JCAP

from PyQt4 import QtGui
from dictionary_helpers import getCol
import datareader
import depositionwindow_data
import graphwindow_data
import profilewindow
import profilecreator
import os
import filename_handler
import process_deposition_data as pdd
import sys
import cPickle as pickle

DATA_FILE_DIR = ''

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
        # data processor is not initialized until FILE_INFO is complete
        self.processor = None
        # save name of file from which application will read
        self.file = self.initReader()
        # if there are no .csv files in working folder, have user
        #   choose file to load
        if not self.file:
            self.loadDataFile(1)
        # check if filename is in valid format
        filenameError = filename_handler.parseFilename(self.file)
        # if not, ask user for experiment parameters
        if filenameError:
            self.requestFileInfo(1)
        # otherwise, finish setting up program
        else:
            self.initData()
        self.initUI()
        
    """ automatically loads last modified data file
        when application launches """
    def initReader(self):
        lastModifiedFile = ''
        lastModifiedTime = 0
        allFiles = os.listdir(DATA_FILE_DIR)
        data = filter(lambda filename: filename.endswith('.csv'), allFiles)
        for filename in data:
            statbuf = os.stat(os.path.join(DATA_FILE_DIR, filename))
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

    """ initializes all elements of program that require experiment
        information (FILE_INFO must be complete) """
    def initData(self):
        filepath = os.path.join(DATA_FILE_DIR, self.file)
        # if application has just been opened
        if not self.processor:
            # initialize data processor (includes reader)           
            self.processor = pdd.ProcessorThread(parent=self, filename=filepath)
            self.processor.lineRead.connect(self.newLineRead)
            self.processor.newData.connect(self.depUpdate)
            self.processor.srcError.connect(self.sourceError)
            self.processor.start()
        # if loading a new file
        else:
            self.processor.newFile(filepath)
        self.initSupplyVars()

    """Initializes any variables that are useful for error checking"""
    def initSupplyVars(self):
        self.errors =[]
        # number of rows read by checkValidity
        self.rowsReadCV = 0
        self.supply = int(filename_handler.FILE_INFO.get("Supply"))

        try:
            if self.supply % 2 == 0:
                self.rfl = getCol("Power Supply" + str(self.supply) + " Rfl Power")
                self.fwd = getCol("Power Supply" + str(self.supply) + " Fwd Power")
                self.dcbias = getCol("Power Supply" + str(self.supply) + " DC Bias")

            if self.supply % 2 == 1:
                self.output_power = getCol("Power Supply" + str(self.supply) + \
                                           " Output Power")
                self.output_voltage = getCol("Power Supply" + str(self.supply) + \
                                             " Output Voltage")
        except IndexError:
            self.processor.end()
            message = "This is not a valid data file.  Please load a new file."
            invalidFileError = QtGui.QMessageBox.warning(None, "Invalid File",
                                                         message)
            self.loadDataFile(1)

    """ if filename is not in correct format, ask user to enter
        experiment parameters manually
        (mode is 1 if called when the application is first opened,
        0 if called when the user loads a new file) """
    def requestFileInfo(self, mode):
        fileErrorDialog = FileInfoDialog(mode)
        self.miscWindows.append(fileErrorDialog)
        fileErrorDialog.fileInfoComplete.connect(self.initData)
        fileErrorDialog.fileAborted.connect(self.loadDataFile)

    """ allows user to choose another data file
        (mode is 1 if called to replace default file,
        0 if the user loads a new file through main menu) """
    def loadDataFile(self, mode=0):
        global DATA_FILE_DIR
        global FILE_INFO
        dirname = QtGui.QFileDialog.getOpenFileName(self, 'Open data file',
                                                      DATA_FILE_DIR,
                                                      'CSV files (*.csv)')
        # if cancel is clicked, dirname will be empty string
        if dirname != '':
            filename_handler.FILE_INFO = {'Element':'', 'Source':'', 'Supply':'', 'TiltDeg':[],
             'Z_mm':[]}
            # converts Qstring to string
            dirString = str(dirname)
            # gets filename from current directory (will be changed eventually)
            dirList = dirString.split('/')
            DATA_FILE_DIR = '/'.join(dirList[:len(dirList)-1])
            self.file = dirList[len(dirList)-1]
            # hides all windows so they can be removed later
            for window in (self.graphWindows + self.depWindows + self.miscWindows):
                window.hide()
            # check filename for correct format
            filenameError = filename_handler.parseFilename(self.file)
            if filenameError:
                self.requestFileInfo(mode)
            # set everything up for the new file being read
            else:
                self.initData()
        # if user declines to use default file and declines to open a
        #   new file, quit the application
        else:
            if mode == 1:
                self.close()

    """ creates window for single graph """
    def makeGraph(self):
        graph = graphwindow_data.GraphWindow()
        self.graphWindows.append(graph)
        graph.show()

    """ shows profile creator window """
    def makeProfile(self):
        profileCreator = profilecreator.ProfileCreator()
        self.miscWindows.append(profileCreator)
        profileCreator.show()

    """ shows load profile window """
    def selectProfile(self):
        try:
            # open file for reading
            savefile = open('saved_profiles.txt', 'rb')
            savedProfiles = pickle.load(savefile)
            savefile.close()
        # this will occur if profiles have never been saved before
        #   and saved_profiles.txt does not exist
        except IOError:
            savedProfiles = []
        menuList = []
        if not savedProfiles:
            error = QtGui.QMessageBox.information(None, "Load Profile Error",
                                                  "There are no saved profiles.")
            return
        # only show profiles with headings that correspond to this file
        for name, varsList in savedProfiles:
            if all(var in datareader.DATA_HEADINGS.values() for var in varsList):
                    self.profiles[name] = varsList
                    menuList += [name]
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
        if self.processor:
            self.processor.end()   
        event.accept()        

    """ handles signal from reader when new line has been read """
    def newLineRead(self, newRow):
        self.updateGraphs(newRow)
        self.checkValidity(newRow)


    # This can be changed to check for errors. Currently it checks one
    # row at a time but it could be changed to use averages
    """ shows an error message if data indicates experiment failure """
    def checkValidity(self, row):
        errors_list = []
        # change the number so that it ignores the errors for the first
        # calibratingNumber of lines we read in case we're callibrating
        calibratingNumber = 30

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
            if opValue < 5: errors_list.append("Output power is below 5.") 

        newErrors = [error for error in errors_list if error not in self.errors]

        # rows read by the checkValidity increased
        self.rowsReadCV +=1
        
        # do not consider these errors if it's for the first bufferNumber lines
        # as it could be callibrating
        if self.rowsReadCV < calibratingNumber:
            newErrors = []
        self.errors += newErrors

        # show error warnings if necessary
        if newErrors:
            message = "You have the following errors: " + " ".join(newErrors)
            self.validityError = QtGui.QErrorMessage()
            self.validityError.setWindowTitle("Power Supply Warning")
            self.validityError.showMessage(message)

    """ kills data processor and prompts user to load new file if
        invalid source number was provided """
    def sourceError(self, srcNum):
        self.processor.end()
        message = "Source %d is not a valid source.  Please load a new file." % srcNum
        srcError = QtGui.QMessageBox.warning(None, "Source Error", message)
        self.loadDataFile(1)

""" custom dialog box to request necessary file info from user """
class FileInfoDialog(QtGui.QWidget):

    #sends signal and mode to MainMenu once all information
    #   has been entered
    fileInfoComplete = pdd.QtCore.pyqtSignal(int)
    # sends signal and mode to MainMenu if user closes dialog
    fileAborted = pdd.QtCore.pyqtSignal(int)

    """ mode is 1 if called when the application is first opened,
        0 if called when the user loads a new file """
    def __init__(self, mode):
        super(FileInfoDialog, self).__init__()
        self.mode = mode
        self.setWindowModality(pdd.QtCore.Qt.ApplicationModal)
        self.initUI()

    """ draws user interface of window """
    def initUI(self):
        self.setWindowTitle('Experiment Information')
        self.layout = QtGui.QVBoxLayout(self)
        self.gridlayout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)
        self.labels = []
        self.lineEdits = []
        # get necessary parameters from FILE_INFO and sort in alphabetical order
        self.tagsList = [tag for tag in filename_handler.FILE_INFO.iteritems()]
        self.tagsList.sort(key = lambda x: x[0])
        self.layout.addWidget(QtGui.QLabel('Please enter values for the following parameters:'))
        # make sub-layout to hold labels and text fields
        self.layout.addLayout(self.gridlayout)
        for i, (tag, val) in enumerate(self.tagsList):
            # allow comma-separated lists for z and t values
            if type(val) == list:
                val = ','.join([str(x) for x in val])
            # add label for this parameter
            self.labels.append(QtGui.QLabel(tag+':'))
            # if a value was obtained from the filename, fill it in the
            #   text input field
            self.lineEdits.append(QtGui.QLineEdit(str(val)))
            self.gridlayout.addWidget(self.labels[i], i, 0)
            self.gridlayout.addWidget(self.lineEdits[i], i, 1)
        self.enter = QtGui.QPushButton('Enter')
        self.enter.setDefault(True)
        self.enter.clicked.connect(self.sendInfo)
        self.layout.addWidget(self.enter, alignment=pdd.QtCore.Qt.AlignRight)
        self.show()

    """ populates FILE_INFO dictionary and sends signal to MainMenu """
    def sendInfo(self):
        global FILE_INFO
        for i, (tag, val) in enumerate(self.tagsList):
            # convert Qstring to string
            newValStr = str(self.lineEdits[i].text())
            # if text input field is blank, bring up an error message
            if not newValStr:
                self.completionError()
                return
            # convert comma-separated entries into list
            if type(filename_handler.FILE_INFO.get(tag)) == list:
                newValStrList = newValStr.split(',')
                try:
                    newValList = [float(x) for x in newValStrList]
                    filename_handler.FILE_INFO[tag] = newValList
                # raise error if z and t aren't decimal values
                except ValueError:
                    self.formatError()
                    return
            # add user input values to FILE_INFO
            else:
                filename_handler.FILE_INFO[tag] = newValStr
        # notify MainMenu that FILE_INFO is complete and close window
        self.fileInfoComplete.emit(self.mode)
        self.hide()

    """ NOTE: We don't check the validity of any of the actual entries
        here because we trust the user to know the parameters of his/her
        own experiment.  Our program doesn't use the element name anywhere,
        but you could easily check if the element name given is an actual
        element by checking if it's a key in the ELEMENTS dictionary.  An
        invalid power supply will raise an error in initSupplyVars in this
        file; an invalid source number will raise an error in process_
        deposition_data, which will be handled by MainMenu (see SourceError).
        If the input t and z values are incorrect, the deposition graph
        will simply be blank. """

    """ brings up an error message if not all fields are filled in """
    def completionError(self):
        message = "Please enter values for all parameters."
        error = QtGui.QMessageBox.warning(self, "Error", message,
                                          QtGui.QMessageBox.Ok)

    """ brings up an error message if z and t entries are invalid """
    def formatError(self):
        message = "Please enter comma-separated decimal values for Z and tilt."
        error = QtGui.QMessageBox.warning(self, "Error", message,
                                          QtGui.QMessageBox.Ok)
        # clear text input fields for z and t
        if error == QtGui.QMessageBox.Ok:
            for i, (tag, val) in enumerate(self.tagsList):
                if type(filename_handler.FILE_INFO.get(tag)) == list:
                    self.lineEdits[i].clear()

    """ nothing to redraw every second """
    def redrawWindow(self):
        pass

    """ confirms that user doesn't want to load data file if
        user tries to close dialog """
    def closeEvent(self, event):
        message = "If you close this window, you will be prompted to open another file."
        response = QtGui.QMessageBox.information(self, "Note", message,
                                                    QtGui.QMessageBox.Ok |
                                                    QtGui.QMessageBox.Cancel)
        if response == QtGui.QMessageBox.Ok:
            self.fileAborted.emit(self.mode)
            event.accept()
        else:
            event.ignore()
        
""" main event loop """
def main():
    global DATA_FILE_DIR
    dirfile = open('DefaultDirectory.txt', 'rb')
    DATA_FILE_DIR = dirfile.readline()
    dirfile.close()
    app = QtGui.QApplication(sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
