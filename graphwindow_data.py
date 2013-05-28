# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/28/2013
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
    - Format of data files
"""

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        

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

        # setup all the layouts - verify that they take in the correct
        # widget  - TODO
        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.gridlayout = QtGui.QGridLayout(self.main_widget)
        self.axeslayout = QtGui.QGridLayout(self.main_widget) 

        # drop down menu
        self.layout.addWidget(self.selectVar)

        # made widgets for layouts
        self.grid_widget = QtGui.QWidget()
        self.grid_widget.setLayout(self.gridlayout)
        self.axes_widget = QtGui.QWidget()
        self.axes_widget.setLayout(self.axeslayout)

        # Input boxes for axes 
        self.Xmin = QtGui.QLineEdit(self)
        self.Xmax = QtGui.QLineEdit(self)
        self.Ymin = QtGui.QLineEdit(self)
        self.Ymax = QtGui.QLineEdit(self)

        # Lables for the input boxes
        self.label_Xmin = QtGui.QLabel('X Min:')
        self.label_Xmax = QtGui.QLabel('X Max:')
        self.label_Ymin = QtGui.QLabel('Y Min:')
        self.label_Ymax = QtGui.QLabel('Y Max:')

        # place the layouts inside the other layouts
        self.layout.addWidget(self.grid_widget)

        # Add items to the grid widget
        self.gridlayout.addWidget(self.graph,0,0)
        self.gridlayout.addWidget(self.axes_widget, 0,1)

        # Set alignments for the widgets
        self.axeslayout.setAlignment(QtCore.Qt.AlignTop)

        # Add items to the axis widget
        self.axeslayout.addWidget(self.label_Xmin)
        self.axeslayout.addWidget(self.Xmin)
        self.axeslayout.addWidget(self.label_Xmax)
        self.axeslayout.addWidget(self.Xmax)
        self.axeslayout.addWidget(self.label_Ymin)
        self.axeslayout.addWidget(self.Ymin)
        self.axeslayout.addWidget(self.label_Ymax)
        self.axeslayout.addWidget(self.Ymax)
        
        
        
        self.setCentralWidget(self.main_widget)
        
        
        self.show()
        print "INIT UI FINISHED"

    def selectGraph(self, varName):
        # clear plot and set parent to None so it can be deleted
        self.graph.clearPlot()
        self.graph.setParent(None)
        
        self.gridlayout.removeWidget(self.graph)
        varString = str(varName)
        self.graph = Graph(self.main_widget, xvarname = "Time",
                           yvarname = varString)
        self.gridlayout.addWidget(self.graph,0,0)
        self.setWindowTitle(varString)
        
    def updateWindow(self): 
        self.graph.updatePlot()

    def createProfile(self):
        self.profileCreator = ProfileCreator()
        self.profileCreator.show()

    


"""def main():
    app = QtGui.QApplication(sys.argv)
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()"""
        
