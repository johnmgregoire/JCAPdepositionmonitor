# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/28/2013
# For JCAP

from graphwindow_data import *
from profilewindow import *

class MainMenu(QtGui.QWidget):

    def __init__(self):
        super(MainMenu, self).__init__()
        self.windows = []
        self.reader = DataReader(parent=self, filename='sample_data.csv')
        self.reader.start()

        self.initUI()

    def initUI(self):
        self.setGeometry(50, 150, 300, 400)
        self.setWindowTitle('Deposition Monitor') # or whatever this application is actually going to be called
        self.layout = QtGui.QVBoxLayout(self)

        # load data file
        # choose graph
        # create profile
        # load profile
        # color wheel

        makeGraphButton = QtGui.QPushButton('Show Graph')
        self.layout.addWidget(makeGraphButton)
        makeGraphButton.clicked.connect(self.makeGraph)

        makeProfileButton = QtGui.QPushButton('Create a New Profile')
        self.layout.addWidget(makeProfileButton)
        makeProfileButton.clicked.connect(self.makeProfile)

        loadProfileButton = QtGui.QPushButton('Load a Saved Profile')
        self.layout.addWidget(loadProfileButton)
        loadProfileButton.clicked.connect(self.loadProfile)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.updateAll)
        # update graph every 1000 milliseconds
        timer.start(1000)

        self.show()

    def makeGraph(self):
        graph = GraphWindow()
        self.windows += [graph]
        graph.show()

    def makeProfile(self):
        profileCreator = ProfileCreator()
        self.windows += [profileCreator]
        profileCreator.show()

    def loadProfile(self):
        savefile = open('saved_profiles.txt', 'rb')
        # eventually will need to distinguish between multiple
        #   saved profiles in the savefile
        varsList = pickle.load(savefile)
        profileWindow = ProfileWindow(varsList)
        self.windows += [profileWindow]
        profileWindow.show()

    def updateAll(self):
        for window in self.windows:
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
