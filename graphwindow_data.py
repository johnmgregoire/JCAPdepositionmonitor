# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/22/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

from datareader import *
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
        not fixable by simply seperating them, probably threading is necessary.

    TO DO:
    - determine condition for reader thread to end
    - take data on certain conditions?
    - try/catch with partial rows (and other places)
    - Where to actually save the profiles
    - Do we want to only run with a file? 
"""

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        reader = DataReader(filename='testcsv.csv')
        reader.start()
        self.initUI()

    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Graph')
        self.activeGraphs = []


        # set up the menu bar and pop up windows
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Options')

        optionsAction = QtGui.QAction('&Add Profile', self)

        #optionsAction.triggered.connect(PROFILE MENU POPS UP)
        # we need a function here to create a ProfileCreator() widget
        optionsMenu.addAction(optionsAction)
    

        
        self.main_widget = QtGui.QWidget(self)
        graph1 = Graph(self.main_widget)
        graph2 = Graph(self.main_widget)

        self.activeGraphs += [graph1]
        self.activeGraphs += [graph2]

        
        l = QtGui.QVBoxLayout(self.main_widget)

        l.addWidget(graph1)
        l.addWidget(graph2)

        self.setCentralWidget(self.main_widget)
        
        #self.setCentralWidget(graph1)
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.windowUpdater)
        
        # update graph every 1000 milliseconds
        timer.start(1000)
        self.show()

    def windowUpdater(self):
        
        for x in self.activeGraphs:
            x.updatePlot()



def main():
    app = QtGui.QApplication(sys.argv) 
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
        
