# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/31/2013
# For JCAP

from depositionwindow_data import *
from graphwindow_data import *
from profilewindow import *
from process_deposition_data import *
import os

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
        # initializes reader on data file
        self.reader = DataReader(parent=self, filename=self.file)
        self.reader.start()
        self.reader.lineRead.connect(self.newLineRead)
        
        self.initUI()

        self.initSupplyVars()


    """Initializes any variables that are useful for error checking"""
    def initSupplyVars(self):
        self.errors =[]
        self.supply = int(FILE_INFO.get("Supply"))
        if self.supply % 2 == 0:
            self.rfl = getCol("Power Supply" + str(self.supply) + " Rfl Power")
            self.fwd = getCol("Power Supply" + str(self.supply) + " Fwd Power")
            self.dcbias = getCol("Power Supply" + str(self.supply) + " DC Bias")

        if self.supply % 2 == 1:
            self.output_power = getCol("Power Supply" + str(self.supply) + " Output Power")
            self.output_voltage = getCol("Power Supply" + str(self.supply) + " Output Voltage")

    """ automatically loads last modified data file
        when application launches """
    def initReader(self):
        targetDir = 'C:/Users/JCAP-HTE/Documents/GitHub/JCAPdepositionmonitor'
        lastModifiedFile = ''
        lastModifiedTime = 0
        # use os.walk() to recursively traverse directories if necessary
        allFiles = os.listdir(targetDir)
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
        self.setWindowTitle('Deposition Monitor') # or whatever this application is actually going to be called
        self.layout = QtGui.QVBoxLayout(self)

        # load data file
        # choose graph [check]
        # create profile [check]
        # load profile [check]
        # color wheel

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

        # initialize the timer that updates all graphs in application
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.redrawAll)
        # update graph every 1000 milliseconds
        timer.start(1000)

        self.show()

    """ allows user to choose another data file """
    def loadDataFile(self):
        dirname = QtGui.QFileDialog.getOpenFileName(self, 'Open data file',
                                                      'C:/Users/JCAP-HTE/Documents/GitHub/JCAPdepositionmonitor',
                                                      'CSV files (*.csv)')
        # if Cancel is clicked, dirname will be empty string
        if dirname != '':
            # converts Qstring to string
            dirString = str(dirname)
            # gets filename from current directory (will be changed eventually)
            dirList = dirString.split('/')
            self.file = dirList[len(dirList)-1]
            self.reader.end()
            # hides all windows so they can be removed later
            for window in zip(self.graphWindows, self.depWindows,
                              self.miscWindows):
                window.hide()
            self.reader = DataReader(parent=self, filename=self.file)
            self.reader.start()
            self.reader.lineRead.connect(self.newLineRead)

            self.initSupplyVars()

    """ creates window for single graph """
    def makeGraph(self):
        graph = GraphWindow(datafile=self.file)
        self.graphWindows.append(graph)
        graph.show()

    """ shows profile creator window """
    def makeProfile(self):
        profileCreator = ProfileCreator(datafile=self.file)
        self.miscWindows.append(profileCreator)
        profileCreator.show()

    """ shows load profile window """
    def selectProfile(self):
        try:
            savefile = open('saved_profiles.txt', 'rb')
        except IOError:
            error = QtGui.QMessageBox.information(None, "Load Profile Error",
                                                  "You have not saved any profiles.")
            return
        menuList = []
        while True:
            # unpickle each profile individually
            try:
                datafile, name, varsList = pickle.load(savefile)
                # only show profiles associated with current data file
                if datafile == self.file:
                    self.profiles[name] = varsList
                    menuList += [name]
            except EOFError:
                break
        loadMenu = LoadMenu(menuList)
        self.miscWindows.append(loadMenu)
        loadMenu.show()
        loadMenu.profileChosen.connect(self.loadProfile)

    """shows the deposition window"""
    def makeDeposition(self):
        depWindow = DepositionWindow()
        self.depWindows.append(depWindow)

    """ once profile is chosen, loads profile in new window """
    def loadProfile(self, name):
        varsList = self.profiles.get(str(name))
        profileWindow = ProfileWindow(name, varsList)
        self.graphWindows.append(profileWindow)
        profileWindow.show()

    """ sends new data received by reader to active graph windows """
    def updateGraphs(self, newRow):
        for window in self.graphWindows:
            window.updateWindow(newRow)

    """ updates all active graph windows every second """
    def redrawAll(self):
        for window in zip(self.graphWindows, self.depWindows,
                          self.miscWindows):
            if window.isHidden():
                self.windows.remove(window)
            else:
                window.redrawWindow()

    """ terminates reader when window is closed """
    def closeEvent(self, event):
        print "signal transmitted"
        self.reader.end()
        event.accept()

    """ handles signal from reader that new line has been read """
    def newLineRead(self, newRow):
        global DEP_DATA
        self.updateGraphs(newRow)
        self.checkValidity(newRow)
        newDepRates = processDataRow(newRow)
        if newDepRates != None:
            DEP_DATA += newDepRates
            for window in self.depWindows:
                window.updateWindow(newDepRates)

    """ Shows an error message is the data is invalid"""
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

        newErrors = [ x for x in errors_list if x not in self.errors]
        self.errors += newErrors
        if newErrors:
            message = "You have the following errors: " + " ".join(newErrors)
            print message
            validityError = QtGui.QMessageBox.information(None,"Unreliable Data Error", message)
            pass
        
""" main event loop """
def main():
    app = QtGui.QApplication(sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
