# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/23/2013
# For JCAP

import datetime
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import *
from datareader import *

""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object, plot, and auto-updating timer """
    def __init__(self, parent="None", width=3, height=2, dpi=100,
                 xvarname="None", yvarname="None"):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.initPlot(xvarname, yvarname)
        FigureCanvas.__init__(self, self.figure)
        # Graph will have a parent widget if contained in a layout
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # variable for sample graph
        self.xLim = 4

    """ draws plot of first variable versus time
        that is displayed when application is opened """
    def initPlot(self, xvarname, yvarname):
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel(xvarname)
        self.axes.set_ylabel(yvarname)

    """ function that updates plot every second """
    def updatePlot(self, xvarname, yvarname):
        yvar = DATA_DICT.get(yvarname)
        list_of_times = []
        for date_string in DATA_DICT.get(xvarname):
            list_of_times += [datetime.datetime.strptime(date_string, "%H:%M:%S.%f")]
        time = matplotlib.dates.date2num(list_of_times)
        self.axes.plot_date(time, yvar) 

        self.draw()
