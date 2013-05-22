# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/21/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

import readers
import sys, csv
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import *

""" Functionality to add:
    - connect to data file
    - get correct column from data file
    - read data file at regular (1 second?) intervals
    - update plot with all new data
    - reset axis labels while maintaining same range (i.e., last 10 minutes)

    Concerns for multiple graphs:
    - threading
    - loading previous data when switching graphs
    - should all graphs be initialized at the beginning, or initialized
        only when clicked on?

    TO DO:
    - determine condition for reader thread to end
    - take data on certain conditions?
    - try/catch with partial rows (and other places)
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
        self.setCentralWidget(Graph(self))
        self.show()


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
                       DATA_DICT[heading] += row[col]
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
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.updatePlot)
        # data received every 1000 milliseconds
        timer.start(1000)

    """ draws sample plot that is displayed when application is opened """
    def initPlot(self):
        self.axes = self.figure.add_subplot(111)

        X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
        C,S = np.cos(X), np.sin(X)

        self.axes.plot(X,C)
        self.axes.plot(X,S)

    """ function that updates sample plot every second """
    def updatePlot(self):
        X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
        C,S = np.cos(X), np.sin(X)

        # increase the x-axis range by 1 every second
        self.xLim += 1
        setp(self.axes, xlim=(-4, self.xLim))
        self.axes.plot(X,C)
        self.axes.plot(X,S)

        self.draw()



def main():
    app = QtGui.QApplication(sys.argv) 
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
        
