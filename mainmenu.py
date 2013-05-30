# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/30/2013
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
        self.defaultFile = self.initReader()
        # initializes reader on data file
        self.reader = DataReader(parent=self, filename=self.defaultFile)
        self.reader.start()
        
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
        timer.timeout.connect(self.updateAll)
        # update graph every 1000 milliseconds
        timer.start(1000)

        self.show()

    """ creates window for single graph """
    def makeGraph(self):
        graph = GraphWindow(datafile=self.defaultFile)
        self.windows += [graph]
        graph.show()

    """ shows profile creator window """
    def makeProfile(self):
        profileCreator = ProfileCreator(datafile=self.defaultFile)
        self.windows += [profileCreator]
        profileCreator.show()

    """ shows load profile window """
    def selectProfile(self):
        savefile = open('saved_profiles.txt', 'rb')
        menuList = []
        while True:
            # unpickle each profile individually
            try:
                datafile, name, varsList = pickle.load(savefile)
                # only show profiles associated with current data file
                if datafile == self.defaultFile:
                    self.profiles[name] = varsList
                    menuList += [name]
            except EOFError:
                break
        loadMenu = LoadMenu(menuList)
        self.windows += [loadMenu]
        loadMenu.show()
        loadMenu.profileChosen.connect(self.loadProfile)

    """ once profile is chosen, loads profile in new window """
    def loadProfile(self, name):
        varsList = self.profiles.get(str(name))
        profileWindow = ProfileWindow(name, varsList)
        self.windows += [profileWindow]
        profileWindow.show()

    """ updates all active windows every second """
    def updateAll(self):
        for window in self.windows:
            if window.isHidden():
                self.windows.remove(window)
            else:
                window.updateWindow()

    """ terminates reader when window is closed """
    def closeEvent(self, event):
        print "signal transmitted"
        self.reader.end()
        event.accept()

""" main event loop """
def main():
    app = QtGui.QApplication(sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
