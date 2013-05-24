# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/24/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

from graph import *
from profilecreator import *

""" Functionality to add:
    - reset axis labels while maintaining same range (i.e., last 10 minutes)

    Concerns for multiple graphs:
    - loading previous data when switching graphs
    - should all graphs be initialized at the beginning, or initialized
        only when clicked on?
    - incomplete set of data in DATA_DICT when graphs are updated
    - Different graphs are affected by terminal/shell activity due to them
        technically being on the same look/update information. This is likely
        not fixable by simply separating them, probably threading is necessary.
        (This is probably not an issue anymore.)

    TO DO:
    - take data on certain conditions?
    - try/catch with partial rows (and other places)
    - fix reader so it doesn't put partial last columns into dictionary

    More things to consider:
    - Is importing a library file more than once dangerous?
    - Should we use a QListWidget for the profile creator?
    - Can we detect when the writer has closed the data file?
    - Does it take up too much processing power to keep reading when
        no new data is being sent?
    - How regularly does information get sent to the data file?
    - Is the data file saved (so we can detect that it's been modified)
        after each write?
"""

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        self.reader = DataReader(parent=self, filename='testcsv.csv')
        self.reader.start()

        self.initUI()

    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 800, 600)
        
        # set up the menu bar and pop up windows
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Options')
        optionsAction = QtGui.QAction('&Add Profile', self)
        optionsAction.triggered.connect(self.createProfile)
        optionsMenu.addAction(optionsAction)
        
        self.main_widget = QtGui.QWidget(self)

        # get variables from spreadsheet
        global DATA_HEADINGS
        self.vars = []
        for index in range(2, len(DATA_HEADINGS)):
            self.vars += [DATA_HEADINGS.get(index)]

        # initialize default graph
        self.graph = Graph(self.main_widget, xvarname="Time",
                           yvarname=self.vars[0])
        self.setWindowTitle(self.vars[0])

        # make drop-down menu for selecting graphs      
        self.selectVar = QtGui.QComboBox()
        for var in self.vars:
            self.selectVar.addItem(var)

        self.selectVar.activated[str].connect(self.selectGraph)
            
        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.layout.addWidget(self.selectVar)
        self.layout.addWidget(self.graph)
        #self.layout.addWidget(graph2)

        self.setCentralWidget(self.main_widget)
        
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.updateWindow)
        
        # update graph every 1000 milliseconds
        timer.start(1000)
        self.show()
        print "INIT UI FINISHED"

    def selectGraph(self, varName):
        self.graph.clearPlot()
        self.layout.removeWidget(self.graph)
        varString = str(varName)
        self.graph = Graph(self.main_widget, xvarname = "Time",
                           yvarname = varString)
        self.layout.addWidget(self.graph)
        self.setWindowTitle(varString)
        
    def updateWindow(self): 
        self.graph.updatePlot()

    def createProfile(self):
        self.profileCreator = ProfileCreator()
        self.profileCreator.launch()

    def closeEvent(self, event):
        print "signal transmitted"
        self.reader.end()
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
        
