# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/21/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

import sys, csv
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import *

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

DATA_DICT = {}
DATA_HEADINGS = {}

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


""" thread that reads data from file """
class DataReader(QtCore.QThread):
    def __init__(self, parent=None, filename='default.csv'):
        super(DataReader, self).__init__()

        self.initData(filename)

    def initData(self, filename):
        self.datafile = open(filename, 'rb')
        # read first line and create data arrays
        headings = self.datafile.readline().split(',')
        self.numColumns = len(headings)
        # strip off '/r/n' at end of line - only works on Windows
        headings[self.numColumns-1] = headings[self.numColumns-1][:-2]
        print headings
        print self.numColumns
        global DATA_DICT
        global DATA_HEADINGS
        for col in range(len(headings)):
            DATA_HEADINGS[col] = headings[col]
            DATA_DICT[headings[col]] = []
        print DATA_HEADINGS
        self.lastEOFpos = self.datafile.tell()

    def run(self):
        partial_rows = False
        partial_row_container = []
        global DATA_DICT
        numColumns = len(DATA_DICT)
        while True:
            # move to position where EOF was previously
            self.datafile.seek(self.lastEOFpos)
            data = csv.reader(self.datafile)
            for row in data:
                """ process colums:
                    check if row is complete
                    if so, add data to each appropriate column array
                    if not, save partial row to local variable container
                    if partial container is full, parse container
                """
                if len(row) == numColumns:
                    for col in range(len(row)):
                       heading = DATA_HEADINGS.get(col)
                       DATA_DICT[heading] += [row[col]]
                    print row
                else:
                    partial_rows = True
                    partial_row_container += row
                    if len(partial_row_container) == numColumns:
                        for col in range(len(partial_row_container)):
                           heading = DATA_HEADINGS.get(col)
                           DATA_DICT[heading] += partial_row_container[col]
                        partial_rows = False
                        print partial_row_container
                        partial_row_container = []
            # save current EOF position
            self.lastEOFpos = self.datafile.tell()


""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object, plot, and auto-updating timer """
    def __init__(self, parent="None", width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.initPlot()
        FigureCanvas.__init__(self, self.figure)
        # Graph will have a parent widget if contained in a layout
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # variable for sample graph
        self.xLim = 4

    """ draws sample plot that is displayed when application is opened """
    def initPlot(self):
        self.axes = self.figure.add_subplot(111)

    """ function that updates sample plot every second """
    def updatePlot(self):
        #self.axes.plot(DATA_DICT['Value'])

        self.draw()

"""widget to make profiles"""
class ProfileCreator(QtGui.QWidget):

    """sets up the Widget"""
    def __init__(self):
        super(ProfileCreator, self).__init__()

        self.initUI()

    def initUI(self):
        pass
        

def main():
    app = QtGui.QApplication(sys.argv) 
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
        
