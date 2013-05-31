# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/31/2013
# For JCAP

from graphwindow_data import *
from profilewindow import *
import os

""" window that pops up when application launches """
class MainMenu(QtGui.QWidget):

    def __init__(self):
        super(MainMenu, self).__init__()
        # holds all active windows
        self.windows = []
        # holds all profiles associated with current file
        self.profiles = {}
        # save name of file from which application will read
        self.file = self.initReader()
        # initializes reader on data file
        self.reader = DataReader(parent=self, filename=self.file)
        self.reader.start()
        self.reader.lineRead.connect(self.newLineRead)
        
        self.initUI()

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
            for window in self.windows:
                window.hide()
            self.reader = DataReader(parent=self, filename=self.file)
            self.reader.start()

    """ creates window for single graph """
    def makeGraph(self):
        graph = GraphWindow(datafile=self.file)
        self.windows.append(graph)
        graph.show()

    """ shows profile creator window """
    def makeProfile(self):
        profileCreator = ProfileCreator(datafile=self.file)
        self.windows.append(profileCreator)
        profileCreator.show()

    """ shows load profile window """
    def selectProfile(self):
        try:
            savefile = open('saved_profiles.txt', 'rb')
        except IOError:
            error = QtGui.QMessageBox.information(None, "Load Profile Error",
                                                  "You have not saved any profiles.")
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
        self.windows.append(loadMenu)
        loadMenu.show()
        loadMenu.profileChosen.connect(self.loadProfile)

    """ once profile is chosen, loads profile in new window """
    def loadProfile(self, name):
        varsList = self.profiles.get(str(name))
        profileWindow = ProfileWindow(name, varsList)
        self.windows.append(profileWindow)
        profileWindow.show()

    """ sends new data received by reader to active graph windows """
    def updateGraphs(self, newRow):
        for window in self.windows:
            window.updateWindow(newRow)

    """ updates all active graph windows every second """
    def redrawAll(self):
        for window in self.windows:
            if window.isHidden():
                self.windows.remove(window)
            else:
                window.redrawWindow()

    """ terminates reader when window is closed """
    def closeEvent(self, event):
        print "signal transmitted"
        self.reader.end()
        event.accept()

### this is currently redundant - can connect signal directly to updateGraphs ###
    def newLineRead(self, newRow):
        #print 'I read a line: ', newRow
        self.updateGraphs(newRow)

""" main event loop """
def main():
    app = QtGui.QApplication(sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
