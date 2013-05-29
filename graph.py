# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/24/2013
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
    def __init__(self, parent="None", width=3, height=2, dpi=80,
                 xvarname="None", yvarname="None"):

        self.updating = True
        self.xvar = xvarname
        self.yvar = yvarname
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.initPlot()
        FigureCanvas.__init__(self, self.figure)
        # Graph will have a parent widget if contained in a layout
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.draw()
        
    """ draws and labels axes """
    def initPlot(self):
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel(self.xvar)
        self.axes.set_ylabel(self.yvar)

    """ function that updates plot every second """
    def updatePlot(self):
        if self.updating == True:
            yvars = DATA_DICT.get(self.yvar)
            list_of_times = []
            for date_string in DATA_DICT.get(self.xvar):
                try:
                    list_of_times += [datetime.datetime.strptime
                                      (date_string, "%H:%M:%S:%f")]
                except ValueError:
                    print "time cut off"
                    pass
            time = matplotlib.dates.date2num(list_of_times)
            try:
                self.axes.plot_date(time, yvars)
            except ValueError:
                print "column not updated: " + self.yvar
                pass

            self.draw()
        else:
            pass

    def hold(self):
        if self.updating == True:
            self.updating = False
        else:
            self.updating = True

    def setXlim(self, amin=None, amax=None):
        self.axes.set_xlim(left=amin, right=amax)

    def setYlim(self, amin=None, amax=None):
        self.axes.set_ylim(bottom=amin, top=amax)

    def clearPlot(self):
        self.figure.clf()
