# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/21/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import *

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()

        self.initUI()

    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Graph')
        self.setCentralWidget(Graph())
        self.show()

""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object, plot, and auto-updating timer """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
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
        # graph updates every 1000 milliseconds
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
        
