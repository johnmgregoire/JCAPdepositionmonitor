# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/28/2013
# For JCAP

from graphwindow_data import *
from profilewindow import *
import os

class MainMenu(QtGui.QWidget):

    def __init__(self):
        super(MainMenu, self).__init__()
        self.windows = []
        self.profiles = {}
        self.defaultFile = self.initReader()
        self.reader = DataReader(parent=self, filename=self.defaultFile)
        self.reader.start()
        
        self.initUI()

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

    def initUI(self):
        self.setGeometry(50, 150, 300, 400)
        self.setWindowTitle('Deposition Monitor') # or whatever this application is actually going to be called
        self.layout = QtGui.QVBoxLayout(self)

        # load data file
        # choose graph [check]
        # create profile [check]
        # load profile [check]
        # color wheel

        makeGraphButton = QtGui.QPushButton('Show Graph')
        self.layout.addWidget(makeGraphButton)
        makeGraphButton.clicked.connect(self.makeGraph)

        makeProfileButton = QtGui.QPushButton('Create a New Profile')
        self.layout.addWidget(makeProfileButton)
        makeProfileButton.clicked.connect(self.makeProfile)

        loadProfileButton = QtGui.QPushButton('Load a Saved Profile')
        self.layout.addWidget(loadProfileButton)
        loadProfileButton.clicked.connect(self.selectProfile)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.updateAll)
        # update graph every 1000 milliseconds
        timer.start(1000)

        self.show()

    def makeGraph(self):
        graph = GraphWindow(datafile=self.defaultFile)
        self.windows += [graph]
        graph.show()

    def makeProfile(self):
        profileCreator = ProfileCreator(datafile=self.defaultFile)
        self.windows += [profileCreator]
        profileCreator.show()

    def selectProfile(self):
        savefile = open('saved_profiles.txt', 'rb')
        menuList = []
        while True:
            try:
                datafile, name, varsList = pickle.load(savefile)
                if datafile == self.defaultFile:
                    self.profiles[name] = varsList
                    menuList += [name]
            except EOFError:
                break
        loadMenu = LoadMenu(menuList)
        self.windows += [loadMenu]
        loadMenu.show()
        loadMenu.profileChosen.connect(self.loadProfile)

    def loadProfile(self, name):
        varsList = self.profiles.get(str(name))
        profileWindow = ProfileWindow(name, varsList)
        self.windows += [profileWindow]
        profileWindow.show()

    def updateAll(self):
        for window in self.windows:
            if window.isHidden():
                self.windows.remove(window)
            else:
                window.updateWindow()

    def closeEvent(self, event):
        print "signal transmitted"
        self.reader.end()
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    menu = MainMenu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
