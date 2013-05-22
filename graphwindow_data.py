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

    THINGS TO LOOK AT TOMORROW:
    - events
    - timer initialized to 0 - what does it actually do?

    -AS, 5/21
"""
    

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        self.initData('testcsv.csv')
        self.initUI()

    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Graph')
        self.setCentralWidget(Graph(self))
        self.show()

    def initData(self, filename):
        readers.followingRead(filename)

# this function was used when data collection ran on its own timer
"""    def updateData(self):
        # move to position where EOF was previously
        self.datafile.seek(self.lastEOFpos)
        data = csv.reader(self.datafile)
        # prints entire row of data for debugging purposes
        for row in data:
            print row
        # save current EOF position
        self.lastEOFpos = self.datafile.tell() """

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
        
